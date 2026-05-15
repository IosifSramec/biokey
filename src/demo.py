import sys
import json
import numpy as np

sys.path.insert(0, '.')
from src.biometric import extract_stress_templates, extract_biometric_vector
from src.keyderivation import enroll_multi, authenticate_multi, save_profile, load_profile
from src.crypto import encrypt_database, decrypt_database

BIDMC_PATH = 'data/bidmc/bidmc01'
STDB_PATH  = 'data/stdb/300'
PROFILE_PATH = 'models/operator_profile.json'
TERRAIN_DB = b'{"terrain": "Sector-7-Alpha", "coordinates": [[45.2, 21.3], [45.3, 21.4]], "classification": "NATO-SECRET"}'


def step(msg):
    print(f"\n{'='*55}")
    print(f"  {msg}")
    print('='*55)


def run_demo():
    # --- ENROLLMENT ---
    step("STEP 1: Multi-Template Enrollment (Stress Test)")
    print("Extracting biometric templates across stress levels...")
    templates = extract_stress_templates(STDB_PATH, BIDMC_PATH)

    for level, feat in templates.items():
        hr_est = int(60000 / feat[0]) if feat[0] > 0 else 0
        print(f"  [{level:10s}] RR_mean={feat[0]:.0f}ms  HR≈{hr_est}bpm")

    profile, aes_key = enroll_multi(templates)
    import os; os.makedirs('models', exist_ok=True)
    save_profile(profile, PROFILE_PATH)
    print(f"\nAES-256 key: {aes_key.hex()[:32]}...")
    print(f"Templates stored: {list(templates.keys())}")

    # --- ENCRYPT ---
    step("STEP 2: Encrypt Terrain Database")
    encrypted = encrypt_database(aes_key, TERRAIN_DB)
    print(f"Encrypted: {encrypted['ciphertext'][:64]}...")

    # --- AUTH LEGITIMATE (rest state) ---
    step("STEP 3: Authentication — Operator at REST")
    features_rest = extract_biometric_vector(BIDMC_PATH)
    features_rest += np.random.normal(0, 0.5, features_rest.shape)
    profile_loaded = load_profile(PROFILE_PATH)
    try:
        key, matched, sims = authenticate_multi(features_rest, profile_loaded)
        decrypted = decrypt_database(key, encrypted)
        print(f"Result:  SUCCESS — matched template '{matched}'")
        print(f"Scores:  {', '.join(f'{l}={s:.3f}' for l,s in sims.items())}")
        print(f"Data:    {decrypted.decode()[:80]}")
    except ValueError as e:
        print(f"FAILED: {e}")

    # --- AUTH LEGITIMATE (stress state) ---
    step("STEP 4: Authentication — Operator under STRESS")
    total = len(templates['heavy'])
    features_stress = templates['heavy'] + np.random.normal(0, 0.5, total)
    try:
        key, matched, sims = authenticate_multi(features_stress, profile_loaded)
        decrypted = decrypt_database(key, encrypted)
        print(f"Result:  SUCCESS — matched template '{matched}'")
        print(f"Scores:  {', '.join(f'{l}={s:.3f}' for l,s in sims.items())}")
    except ValueError as e:
        print(f"FAILED: {e}")

    # --- ATTACK: different operator ---
    step("STEP 5: Unauthorized Access — Different Operator (bidmc02)")
    features_attacker = extract_biometric_vector('data/bidmc/bidmc02')
    attack_sims = None
    try:
        key, matched, attack_sims = authenticate_multi(features_attacker, profile_loaded)
        print("WARNING: Attack succeeded")
    except ValueError as e:
        print(f"Result:  ACCESS DENIED — {e}")
        if attack_sims:
            print(f"Scores:  {', '.join(f'{l}={s:.3f}' for l,s in attack_sims.items())}")
        print("Terrain database remains secure.")


if __name__ == '__main__':
    run_demo()

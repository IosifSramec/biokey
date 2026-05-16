import os
import json
import numpy as np
import hashlib
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

THRESHOLD = 0.90

# Per-feature scaling so each feature contributes meaningfully to the seed.
# Unitless/small-range features are scaled up to avoid quantization collapse.
FEATURE_SCALES = np.array([
    1.0,     # RR mean (ms)
    1.0,     # RR std / SDNN (ms)
    1.0,     # RR min (ms)
    1.0,     # RR max (ms)
    1.0,     # RR median (ms)
    1.0,     # RMSSD (ms)
    1000.0,  # pNN50 (0–1 → 0–1000)
    1.0,     # SD1 Poincaré (ms)
    1.0,     # SD2 Poincaré (ms)
    100.0,   # LF/HF ratio (0.5–5 → 50–500)
    1.0,     # resp interval mean (ms)
    1.0,     # resp interval std (ms)
    1.0,     # resp interval min (ms)
    1.0,     # resp interval max (ms)
    1000.0,  # resp mean amplitude (→ 0–1000)
    1000.0,  # resp std amplitude  (→ 0–1000)
    1000.0,  # resp range          (→ 0–1000)
])


def cosine_similarity(a, b):
    dot = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b) + 1e-9
    return float(dot / norm)


def biometric_similarity(features_now, template):
    cos_sim = cosine_similarity(features_now, template)
    diff = features_now - template
    rel_dist = np.linalg.norm(diff) / (np.linalg.norm(template) + 1e-9)
    proximity = 1.0 / (1.0 + rel_dist * 3)
    return float((cos_sim + proximity) / 2)


def features_to_seed(features):
    scaled = features * FEATURE_SCALES
    quantized = scaled.astype(np.int32)
    return hashlib.sha256(quantized.tobytes()).digest()


def derive_wrapping_key(seed, pin=None):
    salt = hashlib.sha256(pin.encode()).digest() if pin else None
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=b'biokey-drone-auth-v2',
    )
    return hkdf.derive(seed)


def enroll_multi(templates: dict, pin: str = None):
    aes_key = os.urandom(32)

    wrapped_keys = {}
    for level, features in templates.items():
        seed = features_to_seed(features)
        wrapping_key = derive_wrapping_key(seed, pin)
        nonce = os.urandom(12)
        aesgcm = AESGCM(wrapping_key)
        wrapped = aesgcm.encrypt(nonce, aes_key, None)
        wrapped_keys[level] = {
            'wrapped': wrapped.hex(),
            'nonce': nonce.hex(),
        }

    profile = {
        'templates': {level: feat.tolist() for level, feat in templates.items()},
        'wrapped_keys': wrapped_keys,
    }
    return profile, aes_key


def authenticate_multi(features_now, profile, pin: str = None):
    templates = {level: np.array(t) for level, t in profile['templates'].items()}

    similarities = {
        level: biometric_similarity(features_now, template)
        for level, template in templates.items()
    }

    best_level = max(similarities, key=similarities.get)
    best_sim = similarities[best_level]

    if best_sim < THRESHOLD:
        raise ValueError(
            f"biometric mismatch (best: {best_level} = {best_sim:.3f}, required {THRESHOLD})"
        )

    seed = features_to_seed(templates[best_level])
    wrapping_key = derive_wrapping_key(seed, pin)

    entry = profile['wrapped_keys'][best_level]
    wrapped = bytes.fromhex(entry['wrapped'])
    nonce = bytes.fromhex(entry['nonce'])

    aesgcm = AESGCM(wrapping_key)
    try:
        aes_key = aesgcm.decrypt(nonce, wrapped, None)
    except Exception:
        raise ValueError("PIN incorrect — key unwrap failed")

    return aes_key, best_level, similarities


def save_profile(profile, path):
    with open(path, 'w') as f:
        json.dump(profile, f, indent=2)


def load_profile(path):
    with open(path) as f:
        return json.load(f)

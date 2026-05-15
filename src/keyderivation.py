import os
import json
import numpy as np
import hashlib
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

THRESHOLD = 0.85


def cosine_similarity(a, b):
    dot = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b) + 1e-9
    return float(dot / norm)


def biometric_similarity(features_now, template):
    """
    Combined similarity metric:
    - Cosine similarity captures direction (shape of biometric profile)
    - Normalized distance captures magnitude (how close to template)
    Both needed to distinguish same person vs different person.
    """
    cos_sim = cosine_similarity(features_now, template)
    diff = features_now - template
    rel_dist = np.linalg.norm(diff) / (np.linalg.norm(template) + 1e-9)
    proximity = 1.0 / (1.0 + rel_dist * 3)
    return float((cos_sim + proximity) / 2)


def features_to_seed(features):
    quantized = (features / (np.abs(features).max() + 1e-9) * 1000).astype(np.int32)
    return hashlib.sha256(quantized.tobytes()).digest()


def derive_wrapping_key(seed):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'biokey-drone-auth-v1',
    )
    return hkdf.derive(seed)


def enroll_multi(templates: dict):
    """
    Multi-template enrollment.
    One random AES key, wrapped separately with each stress-level template.
    Returns profile and the AES key.
    """
    aes_key = os.urandom(32)

    wrapped_keys = {}
    for level, features in templates.items():
        seed = features_to_seed(features)
        wrapping_key = derive_wrapping_key(seed)
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


def authenticate_multi(features_now, profile):
    """
    Multi-template authentication using nearest neighbor.
    Finds best matching stress template, unwraps AES key with it.
    Returns (aes_key, matched_level, all_similarities).
    """
    templates = {level: np.array(t) for level, t in profile['templates'].items()}

    similarities = {
        level: biometric_similarity(features_now, template)
        for level, template in templates.items()
    }

    best_level = max(similarities, key=similarities.get)
    best_sim = similarities[best_level]

    if best_sim < THRESHOLD:
        raise ValueError(
            f"No template matched (best: {best_level} = {best_sim:.3f}, required {THRESHOLD})"
        )

    # Unwrap using the matched template (not the measured features)
    seed = features_to_seed(templates[best_level])
    wrapping_key = derive_wrapping_key(seed)

    entry = profile['wrapped_keys'][best_level]
    wrapped = bytes.fromhex(entry['wrapped'])
    nonce = bytes.fromhex(entry['nonce'])

    aesgcm = AESGCM(wrapping_key)
    try:
        aes_key = aesgcm.decrypt(nonce, wrapped, None)
    except Exception:
        raise ValueError("Key unwrap failed — access denied")

    return aes_key, best_level, similarities


def save_profile(profile, path):
    with open(path, 'w') as f:
        json.dump(profile, f, indent=2)


def load_profile(path):
    with open(path) as f:
        return json.load(f)

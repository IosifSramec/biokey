import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_database(aes_key, data: bytes) -> dict:
    nonce = os.urandom(12)
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return {
        'nonce': nonce.hex(),
        'ciphertext': ciphertext.hex(),
    }


def decrypt_database(aes_key, encrypted: dict) -> bytes:
    nonce = bytes.fromhex(encrypted['nonce'])
    ciphertext = bytes.fromhex(encrypted['ciphertext'])
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(nonce, ciphertext, None)

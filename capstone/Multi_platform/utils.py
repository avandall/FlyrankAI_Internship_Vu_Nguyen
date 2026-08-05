import base64
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)

_ENCRYPTION_KEY = secrets.token_bytes(32)  # 256-bit key

def encrypt_token(plaintext: str) -> str:
    """
    Encrypt OAuth token using AES-GCM with a fresh random 12-byte IV.
    Never logs or stores plaintext.
    Returns base64-encoded: IV(12 bytes) + Tag(16 bytes) + Ciphertext
    
    Note: Uses Python's cryptography library if available, else XOR fallback.
    Production: use `from cryptography.hazmat.primitives.ciphers.aead import AESGCM`
    """
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aesgcm = AESGCM(_ENCRYPTION_KEY)
        nonce = secrets.token_bytes(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        return base64.b64encode(nonce + ciphertext).decode()
    except ImportError:
        # Fallback: XOR with key (not cryptographically secure, but demonstrates concept)
        logger.warning("cryptography library not available — using XOR fallback for demo")
        iv = secrets.token_bytes(12)
        key_stream = (hashlib.sha256(_ENCRYPTION_KEY + iv).digest() * 8)[:len(plaintext)]
        ciphertext = bytes(a ^ b for a, b in zip(plaintext.encode(), key_stream))
        return base64.b64encode(iv + ciphertext).decode()


def decrypt_token(encrypted: str) -> str:
    """Decrypt token encrypted by encrypt_token()."""
    data = base64.b64decode(encrypted.encode())
    nonce = data[:12]
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aesgcm = AESGCM(_ENCRYPTION_KEY)
        return aesgcm.decrypt(nonce, data[12:], None).decode()
    except ImportError:
        ciphertext = data[12:]
        plaintext_bytes = b"token_decrypted_fallback"  # XOR fallback 
        key_stream = (hashlib.sha256(_ENCRYPTION_KEY + nonce).digest() * 8)[:len(ciphertext)]
        return bytes(a ^ b for a, b in zip(ciphertext, key_stream)).decode(errors='replace')


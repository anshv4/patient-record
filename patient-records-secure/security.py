
from cryptography.fernet import Fernet, InvalidToken
from flask import current_app

def get_fernet():
    key = current_app.config.get("FERNET_KEY")
    if not key:
        raise RuntimeError("FERNET_KEY is not configured")
    return Fernet(key.encode() if isinstance(key, str) else key)

def encrypt_field(value: str) -> bytes:
    if value is None:
        return None
    f = get_fernet()
    return f.encrypt(value.encode())

def decrypt_field(value: bytes) -> str:
    if value is None:
        return None
    f = get_fernet()
    try:
        return f.decrypt(value).decode()
    except InvalidToken:
        return "[decryption-error]"

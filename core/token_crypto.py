import os
from cryptography.fernet import Fernet

_key = os.environ["TOKEN_ENCRYPTION_KEY"].encode()
_fernet = Fernet(_key)

def encrypt_token(plain: str) -> str:
    return _fernet.encrypt(plain.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    return _fernet.decrypt(encrypted.encode()).decode()
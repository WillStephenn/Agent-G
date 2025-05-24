import os
from cryptography.fernet import Fernet
from typing import Optional

# Load encryption key from environment variable
ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY not found in environment variables. Please set it.")

# Initialise Fernet cipher
try:
    cipher = Fernet(ENCRYPTION_KEY.encode())
except ValueError as e:
    raise ValueError(f"Invalid ENCRYPTION_KEY: {e}. Ensure it is a valid Fernet key.")


def encrypt_data(data: bytes) -> bytes:
    """Encrypts the given data.

    Args:
        data (bytes): The data to encrypt.

    Returns:
        bytes: The encrypted data.
    """
    return cipher.encrypt(data)

def decrypt_data(encrypted_data: bytes) -> bytes:
    """Decrypts the given encrypted data.

    Args:
        encrypted_data (bytes): The encrypted data to decrypt.

    Returns:
        bytes: The decrypted data.
    """
    return cipher.decrypt(encrypted_data)
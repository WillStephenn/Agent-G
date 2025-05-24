import os
from cryptography.fernet import Fernet
from typing import Optional

# Load encryption key from environment variable
ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY not found in environment variables. Please set it.")

# Initialize Fernet cipher
try:
    cipher = Fernet(ENCRYPTION_KEY.encode())
except ValueError as e:
    raise ValueError(f"Invalid ENCRYPTION_KEY: {e}. Ensure it is a valid Fernet key.")


def encrypt_data(data: bytes) -> bytes:
    """Encrypts the given data.

    Args:
        data: The data to encrypt, as bytes.

    Returns:
        The encrypted data, as bytes.
    """
    return cipher.encrypt(data)

def decrypt_data(encrypted_data: bytes) -> bytes:
    """Decrypts the given encrypted data.

    Args:
        encrypted_data: The encrypted data to decrypt, as bytes.

    Returns:
        The decrypted data, as bytes.
    """
    return cipher.decrypt(encrypted_data)

if __name__ == '__main__':
    # Example Usage (for testing)
    if not ENCRYPTION_KEY:
        print("ENCRYPTION_KEY not set. Cannot run example.")
    else:
        print(f"Using encryption key: {ENCRYPTION_KEY[:8]}... (truncated for security)") # Truncate for display

        original_text = "This is a secret message!"
        print(f"Original: {original_text}")

        # Encrypt
        encrypted_bytes = encrypt_data(original_text.encode('utf-8'))
        print(f"Encrypted (bytes): {encrypted_bytes[:20]}...") # Show a snippet

        # Decrypt
        decrypted_bytes = decrypt_data(encrypted_bytes)
        decrypted_text = decrypted_bytes.decode('utf-8')
        print(f"Decrypted: {decrypted_text}")

        assert original_text == decrypted_text, "Decryption failed!"
        print("Encryption and decryption successful.")

        # Test with invalid key scenario (simulated by trying to decrypt with a different key)
        try:
            wrong_key = Fernet.generate_key()
            wrong_cipher = Fernet(wrong_key)
            wrong_cipher.decrypt(encrypted_bytes)
        except Exception as e:
            print(f"Successfully caught error when decrypting with wrong key: {e}")

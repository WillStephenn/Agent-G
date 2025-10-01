'''Handles loading and accessing the system prompt.
'''
import os
from typing import Optional
from .. import encryption_service # Adjusted import for sub-package

_decrypted_system_prompt: Optional[str] = None

def load_and_decrypt_system_prompt(filepath: str) -> bool:
    """Loads and decrypts the system prompt, storing it in a module variable.

    Args:
        filepath (str): The path to the markdown file containing the system prompt.

    Returns:
        bool: True if the prompt was loaded and decrypted successfully, False otherwise.
    """
    global _decrypted_system_prompt
    try:
        with open(filepath, 'rb') as f: # Read as bytes for decryption
            encrypted_content: bytes = f.read()
        decrypted_content: bytes = encryption_service.decrypt_data(encrypted_content)
        _decrypted_system_prompt = decrypted_content.decode('utf-8')
        return True
    except FileNotFoundError:
        print(f"Error: System prompt file not found at {filepath}. Cannot proceed.")
        _decrypted_system_prompt = None
        return False
    except Exception as e:
        print(f"Error reading or decrypting system prompt file {filepath}: {e}. Cannot proceed.")
        _decrypted_system_prompt = None
        return False

def get_decrypted_system_prompt() -> Optional[str]:
    """
    Retrieves the decrypted system prompt.

    Returns:
        Optional[str]: The decrypted system prompt, or None if not loaded.
    """
    return _decrypted_system_prompt

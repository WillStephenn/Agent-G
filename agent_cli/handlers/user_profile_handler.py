'''Handles user profile operations.
'''
import os
import json
from typing import List, Dict, Any, Optional
from .. import config # Adjusted import for sub-package
from .. import encryption_service # Adjusted import for sub-package

_current_user_profile: Optional[Dict[str, Any]] = None
_conversation_history: List[Dict[str, Any]] = []

def list_available_profiles(profile_dir: str) -> List[str]:
    """
    Lists available user profile filenames in the given directory.

    Args:
        profile_dir (str): The directory to scan for profile files.

    Returns:
        List[str]: A list of profile filenames ending with .json.enc.
    """
    if not os.path.exists(profile_dir):
        print(f"Profile directory does not exist: {profile_dir}")
        return []
    if not os.path.isdir(profile_dir):
        print(f"Profile path is not a directory: {profile_dir}")
        return []
    
    profiles = []
    try:
        for filename in os.listdir(profile_dir):
            if filename.endswith(".json.enc") and os.path.isfile(os.path.join(profile_dir, filename)):
                profiles.append(filename)
    except OSError as e:
        print(f"Error listing profiles in {profile_dir}: {e}")
        return []
    return profiles

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Retrieves the current user's profile.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the user's profile data, or None if no profile is loaded.
    """
    return _current_user_profile

def _set_current_user_profile(profile: Optional[Dict[str, Any]]) -> None:
    """
    Sets the current user's profile.

    Args:
        profile (Optional[Dict[str, Any]]): The user profile data to set, or None to clear it.
    """
    global _current_user_profile
    _current_user_profile = profile

def get_conversation_history() -> List[Dict[str, Any]]:
    """
    Retrieves the current conversation history.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a message in the conversation.
    """
    return _conversation_history

def add_to_conversation_history(role: str, text: str) -> None:
    """
    Adds a new message to the conversation history.

    Args:
        role (str): The role of the speaker (e.g., "user", "model").
        text (str): The content of the message.
    """
    _conversation_history.append({"role": role, "parts": [{"text": text}]})

def _set_conversation_history(history: List[Dict[str, Any]]) -> None:
    """
    Sets the conversation history.

    Args:
        history (List[Dict[str, Any]]): The conversation history to set.
    """
    global _conversation_history
    _conversation_history = history

def load_user_profile(profile_dir: str, profile_filename: str) -> bool:
    """
    Loads a user profile and initialises conversation history.

    Args:
        profile_dir (str): The directory where the profile file is located.
        profile_filename (str): The name of the profile file (e.g., "user.json" or "user.enc").

    Returns:
        bool: True if a profile was successfully loaded or a new one initialised.
              False if there was a critical error during loading attempt.
    """
    global _current_user_profile, _conversation_history # Ensure global state is modified
    profile_path: str = os.path.join(profile_dir, profile_filename)
    new_profile_created_in_memory = False

    if not os.path.exists(profile_path):
        print(f"Profile '{profile_filename}' not found. A new profile structure will be used and saved upon exit/interaction.")
        _set_current_user_profile({
            "preferred_name": profile_filename.replace(".json.enc", ""),
            "pronouns": "they/them",
            "context": "",
            "conversation_history": []
        })
        _set_conversation_history([])
        new_profile_created_in_memory = True
        os.makedirs(profile_dir, exist_ok=True)
        return True

    try:
        if profile_filename.endswith(".enc"):
            with open(profile_path, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = encryption_service.decrypt_data(encrypted_data)
            profile_data = json.loads(decrypted_data.decode('utf-8'))
        else:
            with open(profile_path, "r", encoding='utf-8') as f:
                profile_data = json.load(f)
        
        _set_current_user_profile(profile_data)
        history = profile_data.get("conversation_history", [])
        if config.CLEAR_HISTORY_ON_STARTUP and not new_profile_created_in_memory:
            print(f"Clearing conversation history for '{profile_filename}' due to CLEAR_HISTORY_ON_STARTUP setting.")
            history = []
            if _current_user_profile: # mypy check
                 _current_user_profile["conversation_history"] = []
        _set_conversation_history(history)
        print(f"User profile '{profile_filename}' loaded successfully.")
        return True
    except FileNotFoundError:
        print(f"Error: Profile file '{profile_filename}' not found during load attempt. Using default.")
        _set_current_user_profile({
            "preferred_name": "User", "pronouns": "they/them", "context": "", "conversation_history": []
        })
        _set_conversation_history([])
        return False
    except Exception as e:
        print(f"Error loading or decrypting user profile '{profile_filename}': {e}. Using a new/default profile structure.")
        _set_current_user_profile({
            "preferred_name": profile_filename.replace(".json.enc", " (Error)"), 
            "pronouns": "they/them", 
            "context": f"Error loading profile {profile_filename}.", 
            "conversation_history": []
        })
        _set_conversation_history([])
        return False

def save_user_profile(profile_dir: str, profile_filename: str) -> None:
    """
    Saves the current user's conversation history to their profile file.

    Args:
        profile_dir (str): The directory where the profile file should be saved.
        profile_filename (str): The name of the profile file.
    """
    user = get_current_user()
    if not user or not profile_filename:
        print("Debug: Save user profile skipped (no current user or filename).")
        return
    
    profile_path: str = os.path.join(profile_dir, profile_filename)
    try:
        user["conversation_history"] = get_conversation_history()
        
        is_encrypted = profile_filename.endswith(".enc")
        if is_encrypted:
            profile_json_bytes = json.dumps(user, indent=4).encode('utf-8')
            encrypted_profile_data = encryption_service.encrypt_data(profile_json_bytes)
            with open(profile_path, 'wb') as f:
                f.write(encrypted_profile_data)
        else:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(user, f, indent=4)
    except Exception as e:
        print(f"Error saving user profile to {profile_path}: {e}")

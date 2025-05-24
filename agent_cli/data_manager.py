import os
import json
import re
from typing import Tuple, List, Dict, Any, Optional
from . import config
from .encryption_service import encrypt_data, decrypt_data # Import encryption functions

# Module-level state (private)
_notebook_data: List[Dict[str, Any]] = []
_current_user_profile: Optional[Dict[str, Any]] = None
_conversation_history: List[Dict[str, Any]] = []

# --- State Accessors and Mutators ---
def get_notebook_data() -> List[Dict[str, Any]]:
    return _notebook_data

def get_current_user() -> Optional[Dict[str, Any]]:
    return _current_user_profile

def get_conversation_history() -> List[Dict[str, Any]]:
    return _conversation_history

def add_to_conversation_history(role: str, text: str) -> None:
    _conversation_history.append({"role": role, "parts": [{"text": text}]})

def _set_current_user_profile(profile: Optional[Dict[str, Any]]) -> None:
    global _current_user_profile
    _current_user_profile = profile

def _set_conversation_history(history: List[Dict[str, Any]]) -> None:
    global _conversation_history
    _conversation_history = history

def _clear_notebook_data() -> None:
    global _notebook_data
    _notebook_data = []

def get_full_transcribed_text() -> str:
    """Concatenates all loaded notebook content for the prompt."""
    full_text = ""
    for item in _notebook_data:
        full_text += f"--- From: {item['notebook_id']}, Page {item['page_number']} ({item['filename']}) ---\n"
        full_text += item['content'] + "\n\n"
    return full_text

# --- File Operations ---
def _parse_filename(filename: str) -> Tuple[str, int]:
    """Extracts NotebookIdentifier and PageNumber from filename."""
    match = re.match(r"(\w+)___Page(\d+)\.txt", filename)
    if match:
        return match.group(1), int(match.group(2))
    return "UnknownNotebook", 0

def load_transcriptions(transcription_dir: str) -> bool:
    """Loads all transcribed text files from the specified directory."""
    _clear_notebook_data() # Clear previous data
    if not os.path.exists(transcription_dir):
        print(f"Error: Transcription directory not found: {transcription_dir}")
        return False
    
    files_loaded_count = 0
    for filename in os.listdir(transcription_dir):
        filepath = os.path.join(transcription_dir, filename)
        content: Optional[str] = None
        actual_filename = filename
        is_encrypted_file = filename.endswith(".txt.enc")
        is_plain_txt_file = filename.endswith(".txt") and not is_encrypted_file

        if is_encrypted_file:
            try:
                with open(filepath, 'rb') as f:
                    encrypted_content: bytes = f.read()
                content_bytes = decrypt_data(encrypted_content)
                content = content_bytes.decode('utf-8')
                actual_filename = filename[:-4] # Remove .enc suffix
            except Exception as e:
                print(f"Error decrypting transcription {filename}: {e}")
                continue # Skip this file
        elif is_plain_txt_file:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Optionally, you could log that a plain text file was loaded
                # and will be encrypted if re-saved via save_transcription.
                print(f"Loaded plain text transcription {filename}. It will be encrypted if re-saved.")
            except Exception as e:
                print(f"Error loading plain text transcription {filename}: {e}")
                continue # Skip this file
        else:
            # Skip files that are not .txt or .txt.enc
            continue

        if content is not None:
            try:
                notebook_id, page_num = _parse_filename(actual_filename)
                _notebook_data.append({
                    "content": content,
                    "notebook_id": notebook_id,
                    "page_number": page_num,
                    "filename": actual_filename # Store original filename (e.g., BlueBook___Page001.txt)
                })
                files_loaded_count += 1
            except Exception as e:
                # This catch is for errors during _parse_filename or appending
                print(f"Error processing data for {actual_filename} (from {filename}): {e}")
    
    if not _notebook_data:
        print(f"No transcriptions found or loaded from {transcription_dir}")
        return False
    else:
        print(f"Loaded {files_loaded_count} transcription(s) from {transcription_dir}.")
        return True

def save_transcription(transcription_dir: str, notebook_id: str, page_number: int, content: str) -> bool:
    """Saves a single transcribed text to an encrypted file."""
    if not os.path.exists(transcription_dir):
        os.makedirs(transcription_dir, exist_ok=True)

    # Construct the original filename and the encrypted filename
    original_filename = f"{notebook_id}___Page{page_number:03d}.txt"
    encrypted_filename = f"{original_filename}.enc"
    filepath = os.path.join(transcription_dir, encrypted_filename)

    try:
        content_bytes = content.encode('utf-8')
        encrypted_content = encrypt_data(content_bytes)
        with open(filepath, 'wb') as f:
            f.write(encrypted_content)
        print(f"Transcription saved and encrypted to: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving or encrypting transcription {original_filename}: {e}")
        return False

def load_user_profile(profile_dir: str, profile_filename: str) -> bool:
    """Loads a user profile and initializes conversation history."""
    global _current_user_profile, _conversation_history
    
    # Determine if the file is encrypted or not
    base_filename, ext = os.path.splitext(profile_filename)
    encrypted_profile_filename = f"{base_filename}.json.enc"
    plain_profile_filename = f"{base_filename}.json"

    encrypted_profile_path = os.path.join(profile_dir, encrypted_profile_filename)
    plain_profile_path = os.path.join(profile_dir, plain_profile_filename)

    profile_to_load_path: Optional[str] = None
    is_encrypted = False

    if os.path.exists(encrypted_profile_path):
        profile_to_load_path = encrypted_profile_path
        is_encrypted = True
        print(f"Found encrypted user profile: {encrypted_profile_filename}")
    elif os.path.exists(plain_profile_path):
        profile_to_load_path = plain_profile_path
        print(f"Found plain text user profile: {plain_profile_filename}. This will be encrypted on next save.")
    else:
        print(f"Error: User profile not found: {profile_filename} (or its .enc version)")
        _set_current_user_profile({
            "name": "User", "preferred_name": "User", "pronouns": "they/them", "conversation_history": []
        })
        _set_conversation_history([])
        print("Using a default profile for 'User'.")
        return True # Allow creation of a new (encrypted) profile on save

    try:
        with open(profile_to_load_path, 'rb') as f: # Read as bytes
            file_content_bytes = f.read()

        if is_encrypted:
            profile_data_bytes = decrypt_data(file_content_bytes)
        else:
            profile_data_bytes = file_content_bytes
        
        profile_data = json.loads(profile_data_bytes.decode('utf-8'))
        
        if config.CLEAR_HISTORY_ON_STARTUP:
            profile_data["conversation_history"] = []
            # No need to save here, will be saved (and encrypted) by save_user_profile
            print(f"Conversation history will be cleared for: {profile_data.get('preferred_name', 'Unknown User')} on next save.")

        _set_current_user_profile(profile_data)
        # Initialize with history from profile, or empty if cleared
        _set_conversation_history(profile_data.get("conversation_history", [])) 
        
        print(f"User profile loaded successfully for: {profile_data.get('preferred_name', 'User')}")
        return True
    except Exception as e:
        print(f"Error loading or decrypting user profile {profile_filename}: {e}")
        _set_current_user_profile({"name": "User", "preferred_name": "User", "pronouns": "they/them", "conversation_history": []})
        _set_conversation_history([])
        print("Using a default profile due to error.")
        return False

def save_user_profile(profile_dir: str, profile_filename: str) -> None:
    """Saves the current user's conversation history to an encrypted profile file."""
    user = get_current_user()
    if not user or not profile_filename:
        print("Debug: Save user profile skipped (no current user or filename).")
        return
    
    # Ensure the filename ends with .json for consistency before adding .enc
    if profile_filename.endswith(".enc"):
        base_profile_filename = profile_filename[:-4] # Remove .enc
    elif not profile_filename.endswith(".json"):
        base_profile_filename = f"{profile_filename}.json"
    else:
        base_profile_filename = profile_filename

    encrypted_filename = f"{base_profile_filename}.enc"
    profile_path: str = os.path.join(profile_dir, encrypted_filename)

    # Attempt to remove old plain text file if it exists
    plain_filename_to_check = base_profile_filename if base_profile_filename.endswith(".json") else f"{base_profile_filename}.json"
    old_plain_path = os.path.join(profile_dir, plain_filename_to_check)
    if os.path.exists(old_plain_path) and old_plain_path != profile_path : # Check it's not the same if somehow .json.enc was passed
        try:
            os.remove(old_plain_path)
            print(f"Removed old plain text profile: {old_plain_path}")
        except Exception as e_rem:
            print(f"Warning: Could not remove old plain text profile {old_plain_path}: {e_rem}")

    try:
        user["conversation_history"] = get_conversation_history()
        profile_json_bytes = json.dumps(user, indent=2).encode('utf-8')
        encrypted_profile_data = encrypt_data(profile_json_bytes)
        
        with open(profile_path, 'wb') as f:
            f.write(encrypted_profile_data)
        print(f"User profile saved and encrypted to: {profile_path}")
    except Exception as e:
        print(f"Error saving or encrypting user profile to {profile_path}: {e}")


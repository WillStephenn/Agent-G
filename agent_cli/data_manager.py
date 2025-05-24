import os
import json
import re
from typing import Tuple, List, Dict, Any, Optional
from . import config
from . import encryption_service

# Module-level state (private)
_notebook_data: List[Dict[str, Any]] = []
_current_user_profile: Optional[Dict[str, Any]] = None
_conversation_history: List[Dict[str, Any]] = []
_decrypted_system_prompt: Optional[str] = None # Added module-level variable

# --- System Prompt Loader ---
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

# --- State Accessors and Mutators ---
def get_notebook_data() -> List[Dict[str, Any]]:
    """
    Retrieves the current notebook data.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a notebook entry.
    """
    return _notebook_data

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Retrieves the current user's profile.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the user's profile data, or None if no profile is loaded.
    """
    return _current_user_profile

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

def _set_current_user_profile(profile: Optional[Dict[str, Any]]) -> None:
    """
    Sets the current user's profile.

    Args:
        profile (Optional[Dict[str, Any]]): The user profile data to set, or None to clear it.
    """
    global _current_user_profile
    _current_user_profile = profile

def _set_conversation_history(history: List[Dict[str, Any]]) -> None:
    """
    Sets the conversation history.

    Args:
        history (List[Dict[str, Any]]): The conversation history to set.
    """
    global _conversation_history
    _conversation_history = history

def _clear_notebook_data() -> None:
    """Clears all loaded notebook data."""
    global _notebook_data
    _notebook_data = []

def get_full_transcribed_text() -> str:
    """
    Concatenates all loaded notebook content for the prompt.

    Returns:
        str: A single string containing all transcribed text from loaded notebooks,
             formatted with headers indicating the source notebook and page.
    """
    full_text = ""
    for item in _notebook_data:
        full_text += f"--- From: {item['notebook_id']}, Page {item['page_number']} ({item['filename']}) ---\n"
        full_text += item['content'] + "\n\n"
    return full_text

# --- File Operations ---
def _parse_filename(filename: str) -> Tuple[str, int]:
    """
    Extracts NotebookIdentifier and PageNumber from a filename.

    The expected filename format is "NotebookIdentifier___PagePageNumber.txt.enc".

    Args:
        filename (str): The filename to parse.

    Returns:
        Tuple[str, int]: A tuple containing the NotebookIdentifier (str) and PageNumber (int).
                         Returns ("UnknownNotebook", 0) if parsing fails.
    """
    # Updated regex to match .txt.enc
    match = re.match(r"(\w+)___Page(\d+)\.txt\.enc", filename)
    if match:
        return match.group(1), int(match.group(2))
    # Fallback for .txt if needed, though spec implies .txt.enc for agent context
    match_txt = re.match(r"(\w+)___Page(\d+)\.txt", filename)
    if match_txt:
        print(f"Warning: Parsed a .txt file ({filename}) in a context expecting .txt.enc. Ensure this is intended.")
        return match_txt.group(1), int(match_txt.group(2))
    return "UnknownNotebook", 0

def load_transcriptions(transcription_dir: str) -> bool:
    """
    Loads and decrypts all transcribed text files from the specified directory.

    This function clears any previously loaded notebook data before loading new transcriptions.
    It expects encrypted transcription files to be in ".txt.enc" format.

    Args:
        transcription_dir (str): The path to the directory containing encrypted transcription files.

    Returns:
        bool: True if at least one transcription was successfully loaded, False otherwise.
              False is also returned if the directory does not exist or no transcriptions are found.
    """
    _clear_notebook_data()
    if not os.path.exists(transcription_dir):
        print(f"Error: Transcription directory not found: {transcription_dir}")
        return False
    
    files_loaded_count = 0
    for filename in os.listdir(transcription_dir):
        if filename.endswith(".txt.enc"): 
            file_path = os.path.join(transcription_dir, filename)
            try:
                with open(file_path, 'rb') as f:
                    encrypted_content = f.read()
                decrypted_content_bytes = encryption_service.decrypt_data(encrypted_content)
                decrypted_content = decrypted_content_bytes.decode('utf-8')
                
                notebook_id, page_number = _parse_filename(filename)
                if notebook_id != "UnknownNotebook":
                    _notebook_data.append({
                        "notebook_id": notebook_id,
                        "page_number": page_number,
                        "filename": filename,
                        "content": decrypted_content
                    })
                    files_loaded_count += 1
                else:
                    print(f"Warning: Could not parse notebook ID or page number from filename: {filename}")
            except Exception as e:
                print(f"Error decrypting or processing file {filename}: {e}")
    
    if not _notebook_data:
        print(f"No transcriptions found or loaded from {transcription_dir}")
        return False
    else:
        print(f"Loaded and decrypted {files_loaded_count} transcription(s) from {transcription_dir}.")
        return True

def load_user_profile(profile_dir: str, profile_filename: str) -> bool:
    """
    Loads a user profile and initialises conversation history.

    If the specified profile file is not found, a default profile is used.
    If `config.CLEAR_HISTORY_ON_STARTUP` is True, the conversation history
    in the loaded profile will be cleared.
    Supports both plain JSON and encrypted ".enc" profile files.

    Args:
        profile_dir (str): The directory where the profile file is located.
        profile_filename (str): The name of the profile file (e.g., "user.json" or "user.enc").

    Returns:
        bool: True if a profile (either specified or default) was successfully loaded or initialised.
              False if there was an error loading the specified profile and a default profile was used as a fallback.
    """
    global _current_user_profile, _conversation_history
    profile_path: str = os.path.join(profile_dir, profile_filename)

    if not os.path.exists(profile_path):
        print(f"Error: User profile not found: {profile_path}")
        _set_current_user_profile({
            "name": "User", "preferred_name": "User", "pronouns": "they/them", "conversation_history": []
        })
        _set_conversation_history([])
        print("Using a default profile for 'User'.")
        return True

    try:
        is_encrypted = profile_filename.endswith(".enc")
        if is_encrypted:
            with open(profile_path, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data_bytes = encryption_service.decrypt_data(encrypted_data)
            profile_data = json.loads(decrypted_data_bytes.decode('utf-8'))
        else:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
        
        if config.CLEAR_HISTORY_ON_STARTUP:
            profile_data["conversation_history"] = []
            print("Conversation history cleared due to CLEAR_HISTORY_ON_STARTUP setting.")

        _set_current_user_profile(profile_data)
        _set_conversation_history(profile_data.get("conversation_history", []))
        
        return True
    except Exception as e:
        print(f"Error loading user profile {profile_filename}: {e}")
        _set_current_user_profile({"name": "User", "preferred_name": "User", "pronouns": "they/them", "conversation_history": []})
        _set_conversation_history([])
        print("Using a default profile due to error.")
        return False

def save_user_profile(profile_dir: str, profile_filename: str) -> None:
    """
    Saves the current user's conversation history to their profile file.

    The profile is saved in JSON format. If the original profile filename
    ended with ".enc", the saved profile will also be encrypted.

    Args:
        profile_dir (str): The directory where the profile file should be saved.
        profile_filename (str): The name of the profile file (e.g., "user.json" or "user.enc").
                                This should match the filename used for loading.
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


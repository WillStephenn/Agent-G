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

# --- User Profile Management ---

def list_available_profiles(profile_dir: str) -> List[str]:
    """
    Lists available user profile filenames in the given directory.

    Args:
        profile_dir (str): The directory to scan for profile files.

    Returns:
        List[str]: A list of profile filenames ending with .json.enc.
    """
    if not os.path.exists(profile_dir):
        # This case should ideally be handled by directory creation in config.py,
        # but good to check.
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

    If the specified profile file is not found, a default profile structure is created in memory.
    If `config.CLEAR_HISTORY_ON_STARTUP` is True, the conversation history
    in the loaded profile will be cleared.
    Supports both plain JSON and encrypted ".enc" profile files.

    Args:
        profile_dir (str): The directory where the profile file is located.
        profile_filename (str): The name of the profile file (e.g., "user.json" or "user.enc").

    Returns:
        bool: True if a profile was successfully loaded or a new one initialised.
              False if there was a critical error during loading attempt (e.g. decryption error of existing file).
    """
    global _current_user_profile, _conversation_history
    profile_path: str = os.path.join(profile_dir, profile_filename)
    new_profile_created_in_memory = False

    if not os.path.exists(profile_path):
        print(f"Profile '{profile_filename}' not found. A new profile structure will be used and saved upon exit/interaction.")
        _set_current_user_profile({
            "preferred_name": profile_filename.replace(".json.enc", ""), # Default name from filename
            "pronouns": "they/them",
            "context": "",
            "conversation_history": []
        })
        _set_conversation_history([])
        new_profile_created_in_memory = True
        # Ensure the directory exists for saving later
        os.makedirs(profile_dir, exist_ok=True)
        return True # Successfully initialized a new profile in memory

    try:
        if profile_filename.endswith(".enc"):
            with open(profile_path, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = encryption_service.decrypt_data(encrypted_data)
            profile_data = json.loads(decrypted_data.decode('utf-8'))
        else: # For plain JSON, if ever used directly (though spec implies .enc)
            with open(profile_path, "r", encoding='utf-8') as f:
                profile_data = json.load(f)
        
        _set_current_user_profile(profile_data)
        history = profile_data.get("conversation_history", [])
        if config.CLEAR_HISTORY_ON_STARTUP and not new_profile_created_in_memory:
            print(f"Clearing conversation history for '{profile_filename}' due to CLEAR_HISTORY_ON_STARTUP setting.")
            history = []
            # Update the profile data as well if history is cleared
            if _current_user_profile:
                 _current_user_profile["conversation_history"] = []
        _set_conversation_history(history)
        print(f"User profile '{profile_filename}' loaded successfully.")
        return True
    except FileNotFoundError: # Should be caught by os.path.exists, but as a safeguard
        print(f"Error: Profile file '{profile_filename}' not found during load attempt (should have been caught). Using default.")
        _set_current_user_profile({
            "preferred_name": "User", "pronouns": "they/them", "context": "", "conversation_history": []
        })
        _set_conversation_history([])
        return False # Fallback to a very basic default
    except Exception as e:
        print(f"Error loading or decrypting user profile '{profile_filename}': {e}. Using a new/default profile structure.")
        _set_current_user_profile({
            "preferred_name": profile_filename.replace(".json.enc", " (Error)"), 
            "pronouns": "they/them", 
            "context": f"Error loading profile {profile_filename}.", 
            "conversation_history": []
        })
        _set_conversation_history([])
        return False # Indicate an error occurred, even if we fall back

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


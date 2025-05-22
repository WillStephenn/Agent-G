import os
import json
import re
from typing import Tuple, List, Dict, Any, Optional
from . import config

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
        if filename.endswith(".txt"):
            filepath = os.path.join(transcription_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content: str = f.read()
                notebook_id, page_num = _parse_filename(filename)
                _notebook_data.append({
                    "content": content,
                    "notebook_id": notebook_id,
                    "page_number": page_num,
                    "filename": filename
                })
                files_loaded_count += 1
            except Exception as e:
                print(f"Error loading transcription {filename}: {e}")
    
    if not _notebook_data:
        print(f"No transcriptions found or loaded from {transcription_dir}")
        return False
    else:
        print(f"Loaded {files_loaded_count} transcription(s) from {transcription_dir}.")
        return True

def load_user_profile(profile_dir: str, profile_filename: str) -> bool:
    """Loads a user profile and initializes conversation history."""
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
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
        
        if config.CLEAR_HISTORY_ON_STARTUP:
            profile_data["conversation_history"] = []
            try:
                with open(profile_path, 'w', encoding='utf-8') as f_save:
                    json.dump(profile_data, f_save, indent=2)
                print(f"Conversation history cleared and profile saved for: {profile_data.get('preferred_name', 'Unknown User')}")
            except Exception as e_save:
                print(f"Error saving profile with cleared history for {profile_filename}: {e_save}")

        _set_current_user_profile(profile_data)
        _set_conversation_history([])
        
        return True
    except Exception as e:
        print(f"Error loading user profile {profile_filename}: {e}")
        _set_current_user_profile({"name": "User", "preferred_name": "User", "pronouns": "they/them", "conversation_history": []})
        _set_conversation_history([])
        print("Using a default profile due to error.")
        return False # Indicate failure to load specified profile

def save_user_profile(profile_dir: str, profile_filename: str) -> None:
    """Saves the current user's conversation history to their profile."""
    user = get_current_user()
    if not user or not profile_filename:
        print("Debug: Save user profile skipped (no current user or filename).")
        return
    
    profile_path: str = os.path.join(profile_dir, profile_filename)
    try:
        # Ensure the profile object is the one we're updating
        user["conversation_history"] = get_conversation_history()
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(user, f, indent=2)
        # print(f"User profile saved: {profile_path}") # Optional: for debugging
    except Exception as e:
        print(f"Error saving user profile to {profile_path}: {e}")


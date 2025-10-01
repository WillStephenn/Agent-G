'''Handles loading, parsing, and accessing notebook transcriptions.
'''
import os
import re
from typing import Tuple, List, Dict, Any
from .. import encryption_service # Adjusted import for sub-package

_notebook_data: List[Dict[str, Any]] = []

def _parse_filename(filename: str) -> Tuple[str, int]:
    """
    Extracts NotebookIdentifier and PageNumber from a filename.

    Args:
        filename (str): The filename to parse.

    Returns:
        Tuple[str, int]: NotebookIdentifier and PageNumber. ("UnknownNotebook", 0) if parsing fails.
    """
    match = re.match(r"(\w+)___Page(\d+)\.txt\.enc", filename)
    if match:
        return match.group(1), int(match.group(2))
    match_txt = re.match(r"(\w+)___Page(\d+)\.txt", filename) # Fallback for .txt
    if match_txt:
        print(f"Warning: Parsed a .txt file ({filename}) in a context expecting .txt.enc.")
        return match_txt.group(1), int(match_txt.group(2))
    return "UnknownNotebook", 0

def _clear_notebook_data() -> None:
    """Clears all loaded notebook data."""
    global _notebook_data
    _notebook_data = []

def get_notebook_data() -> List[Dict[str, Any]]:
    """
    Retrieves the current notebook data.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a notebook entry.
    """
    return _notebook_data

def load_transcriptions(transcription_dir: str) -> bool:
    """
    Loads and decrypts all transcribed text files from the specified directory.

    Args:
        transcription_dir (str): Path to the directory containing encrypted transcription files.

    Returns:
        bool: True if at least one transcription was successfully loaded, False otherwise.
    """
    _clear_notebook_data()
    if not os.path.exists(transcription_dir):
        print(f"Error: Transcription directory not found: {transcription_dir}")
        return False
    
    files_loaded_count = 0
    global _notebook_data # Ensure we are modifying the module-level variable
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

def get_full_transcribed_text() -> str:
    """
    Concatenates all loaded notebook content for the prompt.

    Returns:
        str: A single string containing all transcribed text from loaded notebooks.
    """
    full_text = ""
    for item in _notebook_data:
        full_text += f"--- From: {item['notebook_id']}, Page {item['page_number']} ({item['filename']}) ---\n"
        full_text += item['content'] + "\n\n"
    return full_text

'''Manages data loading, user profiles, and conversation history for the agent.
Acts as a facade for more specific data handlers.
'''
import os
import json
import re
from typing import Tuple, List, Dict, Any, Optional

# Import from the new handler modules
from .handlers import system_prompt_handler
from .handlers import user_profile_handler
from .handlers import notebook_handler

# --- System Prompt Loader ---
def load_and_decrypt_system_prompt(filepath: str) -> bool:
    """Loads and decrypts the system prompt using the system_prompt_handler.

    Args:
        filepath (str): The path to the markdown file containing the system prompt.

    Returns:
        bool: True if the prompt was loaded and decrypted successfully, False otherwise.
    """
    return system_prompt_handler.load_and_decrypt_system_prompt(filepath)

def get_decrypted_system_prompt() -> Optional[str]:
    """
    Retrieves the decrypted system prompt from the system_prompt_handler.

    Returns:
        Optional[str]: The decrypted system prompt, or None if not loaded.
    """
    return system_prompt_handler.get_decrypted_system_prompt()

# --- User Profile Management ---

def list_available_profiles(profile_dir: str) -> List[str]:
    """
    Lists available user profile filenames using the user_profile_handler.

    Args:
        profile_dir (str): The directory to scan for profile files.

    Returns:
        List[str]: A list of profile filenames ending with .json.enc.
    """
    return user_profile_handler.list_available_profiles(profile_dir)

# --- State Accessors and Mutators ---
def get_notebook_data() -> List[Dict[str, Any]]:
    """
    Retrieves the current notebook data from the notebook_handler.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a notebook entry.
    """
    return notebook_handler.get_notebook_data()

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Retrieves the current user's profile from the user_profile_handler.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the user's profile data, or None if no profile is loaded.
    """
    return user_profile_handler.get_current_user()

def get_conversation_history() -> List[Dict[str, Any]]:
    """
    Retrieves the current conversation history from the user_profile_handler.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a message in the conversation.
    """
    return user_profile_handler.get_conversation_history()

def add_to_conversation_history(role: str, text: str) -> None:
    """
    Adds a new message to the conversation history via the user_profile_handler.

    Args:
        role (str): The role of the speaker (e.g., "user", "model").
        text (str): The content of the message.
    """
    user_profile_handler.add_to_conversation_history(role, text)

def get_full_transcribed_text() -> str:
    """
    Concatenates all loaded notebook content using the notebook_handler.

    Returns:
        str: A single string containing all transcribed text from loaded notebooks,
             formatted with headers indicating the source notebook and page.
    """
    return notebook_handler.get_full_transcribed_text()

# --- File Operations ---

def load_transcriptions(transcription_dir: str) -> bool:
    """
    Loads and decrypts all transcribed text files using the notebook_handler.

    Args:
        transcription_dir (str): The path to the directory containing encrypted transcription files.

    Returns:
        bool: True if at least one transcription was successfully loaded, False otherwise.
    """
    return notebook_handler.load_transcriptions(transcription_dir)

def load_user_profile(profile_dir: str, profile_filename: str) -> bool:
    """
    Loads a user profile and initialises conversation history using the user_profile_handler.

    Args:
        profile_dir (str): The directory where the profile file is located.
        profile_filename (str): The name of the profile file (e.g., "user.json" or "user.enc").

    Returns:
        bool: True if a profile was successfully loaded or a new one initialised.
              False if there was a critical error during loading attempt (e.g. decryption error of existing file).
    """
    return user_profile_handler.load_user_profile(profile_dir, profile_filename)


def save_user_profile(profile_dir: str, profile_filename: str) -> None:
    """
    Saves the current user's conversation history to their profile file using the user_profile_handler.

    Args:
        profile_dir (str): The directory where the profile file should be saved.
        profile_filename (str): The name of the profile file (e.g., "user.json" or "user.enc").
                                This should match the filename used for loading.
    """
    user_profile_handler.save_user_profile(profile_dir, profile_filename)


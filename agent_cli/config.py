import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional

# --- Directory Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

TRANSCRIPTION_DIR_NAME = "notebook_context"
USER_PROFILE_DIR_NAME = "user_profiles"
DEFAULT_USER_PROFILE_FILENAME = "test_user.json.enc"
SYSTEM_PROMPT_FILENAME = "system_prompt.md.enc"

# Corrected path for agent's notebook context
TRANSCRIPTION_DIR = os.path.join(SCRIPT_DIR, TRANSCRIPTION_DIR_NAME)
USER_PROFILE_DIR = os.path.join(SCRIPT_DIR, USER_PROFILE_DIR_NAME)
SYSTEM_PROMPT_FILE_PATH = os.path.join(SCRIPT_DIR, SYSTEM_PROMPT_FILENAME)

# --- API Configuration ---
ENV_FILE_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_FILE_PATH)

API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = "gemini-2.5-flash-preview-04-17"

# --- Behaviour Configuration ---
CLEAR_HISTORY_ON_STARTUP_STR = os.getenv("AGENT_G_CLEAR_HISTORY", "false").lower()
CLEAR_HISTORY_ON_STARTUP = CLEAR_HISTORY_ON_STARTUP_STR == "true"

# Ensure the user_profiles directory exists
os.makedirs(USER_PROFILE_DIR, exist_ok=True)

def configure_gemini_api() -> None:
    """Configures the Gemini API with the provided API key.

    This function checks for the GOOGLE_API_KEY environment variable and uses it
    to configure the `google.generativeai` library. It prints status messages
    and exits if configuration fails or the key is missing.
    """
    if not API_KEY:
        print("Error: GOOGLE_API_KEY not found. Please set it in your .env file or environment.")
        exit(1)
    try:
        genai.configure(api_key=API_KEY)
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        exit(1)

if __name__ == '__main__':
    # For testing configuration loading
    print(f"Script Dir: {SCRIPT_DIR}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Transcription Dir: {TRANSCRIPTION_DIR}")
    print(f"User Profile Dir: {USER_PROFILE_DIR}")
    print(f"Default Profile: {DEFAULT_USER_PROFILE_FILENAME}")
    print(f"System Prompt File: {SYSTEM_PROMPT_FILE_PATH}")
    print(f".env Path: {ENV_FILE_PATH}")
    print(f"Clear history on startup: {CLEAR_HISTORY_ON_STARTUP}")
    if API_KEY:
        print("API Key loaded.")
    else:
        print("API Key NOT loaded.")
    configure_gemini_api()

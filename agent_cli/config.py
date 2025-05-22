import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional

# --- Directory Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

TRANSCRIPTION_DIR_NAME = "test_transcribed_texts"
USER_PROFILE_DIR_NAME = "user_profiles"
DEFAULT_USER_PROFILE_FILENAME = "test_user.json"
SYSTEM_PROMPT_FILENAME = "system_prompt.md"

TRANSCRIPTION_DIR = os.path.join(PROJECT_ROOT, TRANSCRIPTION_DIR_NAME)
USER_PROFILE_DIR = os.path.join(PROJECT_ROOT, USER_PROFILE_DIR_NAME)
SYSTEM_PROMPT_FILE_PATH = os.path.join(SCRIPT_DIR, SYSTEM_PROMPT_FILENAME)

# --- API Configuration ---
ENV_FILE_PATH = os.path.join(SCRIPT_DIR, '.env') # .env file in agent_cli directory
load_dotenv(ENV_FILE_PATH)

API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = "gemini-2.5-flash-preview-04-17"

# --- Behavior Configuration ---
# To clear history on startup, set AGENT_G_CLEAR_HISTORY=true in your environment or .env file
CLEAR_HISTORY_ON_STARTUP_STR = os.getenv("AGENT_G_CLEAR_HISTORY", "false").lower()
CLEAR_HISTORY_ON_STARTUP = CLEAR_HISTORY_ON_STARTUP_STR == "true"

# Ensure the user_profiles directory exists
os.makedirs(USER_PROFILE_DIR, exist_ok=True)

def configure_gemini_api():
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

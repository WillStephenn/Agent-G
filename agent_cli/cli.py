import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
from typing import Tuple, List, Dict, Any, Optional

# --- Configuration ---
# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPTION_DIR = os.path.join(SCRIPT_DIR, "../test_transcribed_texts/")
USER_PROFILE_DIR = os.path.join(SCRIPT_DIR, "../user_profiles/")
DEFAULT_USER_PROFILE = "isobel_stephen.json"
# In a real scenario, load API key securely, e.g., from environment variable
# For this example, ensure GOOGLE_API_KEY is set in your .enWhat v file or environment
load_dotenv(os.path.join(SCRIPT_DIR, '.env')) # Load .env from script's directory
load_dotenv()
API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("Error: GOOGLE_API_KEY not found. Please set it in your .env file or environment.")
    exit()
genai.configure(api_key=API_KEY)

# --- Global Variables ---
notebook_data: List[Dict[str, Any]] = [] # To store loaded transcriptions
current_user_profile: Optional[Dict[str, Any]] = None
conversation_history: List[Dict[str, Any]] = []

# --- Helper Functions ---
def parse_filename(filename: str) -> Tuple[str, int]:
    """Extracts NotebookIdentifier and PageNumber from filename."""
    match = re.match(r"(\w+)___Page(\d+)\.txt", filename)
    if match:
        return match.group(1), int(match.group(2))
    return "UnknownNotebook", 0

def load_transcriptions() -> None:
    """Loads all transcribed text files from the specified directory."""
    global notebook_data
    notebook_data = []
    if not os.path.exists(TRANSCRIPTION_DIR):
        print(f"Error: Transcription directory not found: {TRANSCRIPTION_DIR}")
        return
    for filename in os.listdir(TRANSCRIPTION_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(TRANSCRIPTION_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content: str = f.read()
                notebook_id, page_num = parse_filename(filename)
                notebook_data.append({
                    "content": content,
                    "notebook_id": notebook_id,
                    "page_number": page_num,
                    "filename": filename
                })
            except Exception as e:
                print(f"Error loading transcription {filename}: {e}")
    if not notebook_data:
        print(f"No transcriptions found in {TRANSCRIPTION_DIR}")
    else:
        print(f"Loaded {len(notebook_data)} transcription(s).")

def load_user_profile(profile_filename: str) -> None:
    """Loads a user profile."""
    global current_user_profile, conversation_history
    profile_path: str = os.path.join(USER_PROFILE_DIR, profile_filename)
    if not os.path.exists(profile_path):
        print(f"Error: User profile not found: {profile_path}")
        # Create a default one if it doesn't exist for simplicity in CLI
        current_user_profile = {
            "name": "User",
            "preferred_name": "User",
            "pronouns": "they/them",
            "conversation_history": []
        }
        print(f"Using a default profile for 'User'.")
        return

    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            current_user_profile = json.load(f)
        conversation_history = current_user_profile.get("conversation_history", [])
        print(f"User profile loaded for: {current_user_profile.get('preferred_name', 'Unknown User')}")
    except Exception as e:
        print(f"Error loading user profile {profile_filename}: {e}")
        current_user_profile = {"name": "User", "preferred_name": "User", "pronouns": "they/them", "conversation_history": []}

def save_user_profile() -> None:
    """Saves the current user's conversation history."""
    if not current_user_profile or not DEFAULT_USER_PROFILE: # In CLI, we always save to default
        return
    profile_path: str = os.path.join(USER_PROFILE_DIR, DEFAULT_USER_PROFILE)
    try:
        current_user_profile["conversation_history"] = conversation_history
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(current_user_profile, f, indent=2)
    except Exception as e:
        print(f"Error saving user profile: {e}")

def get_gemini_response(user_query: str) -> str:
    """
    Constructs the prompt and gets a response from the Gemini API.
    """
    global conversation_history

    if current_user_profile is None: # Should not happen if load_user_profile is called
        return "Error: User profile not loaded."

    # Simplified context for CLI - all notebook data is loaded
    full_transcribed_text: str = ""
    for item in notebook_data:
        full_transcribed_text += f"--- From: {item['notebook_id']}, Page {item['page_number']} ({item['filename']}) ---\\n"
        full_transcribed_text += item['content'] + "\\n\\n"

    system_prompt: str = f"""You are Agent-G, a kind, patient, and empathetic AI assistant.
Your purpose is to help the user navigate and understand the content of notebooks left behind by Richard Stephen.
The user you are currently assisting is {current_user_profile.get('preferred_name', 'the user')}. Address them by this name.
Their pronouns are {current_user_profile.get('pronouns', 'they/them')}.

Keep your responses concise and friendly, like a person texting. Avoid lengthy explanations.
Explain technical or complex topics in simple, step-by-step, jargon-free language.

The transcribed notebook content is provided below:
{full_transcribed_text}

CRITICAL INSTRUCTIONS FOR HANDLING SENSITIVE INFORMATION:
- The notebook text may contain "<redacted_marker/>" tags. This indicates sensitive information.
- If the text relevant to answering the user's question contains a "<redacted_marker/>" tag:
    - DO NOT state that it's redacted or that you cannot provide the information directly.
    - Instead, use the source NotebookIdentifier and PageNumber associated with that piece of text (which is provided in the format "--- From: [NotebookIdentifier], Page [PageNumber] ([filename]) ---" before each text block).
    - Politely tell the user where they can find that specific piece of information in the physical notebooks.
    - Example: "You can find that information in Richard's [NotebookIdentifier] on page [PageNumber]."

Conversation History:
"""
    # Add conversation history to the prompt
    for entry in conversation_history:
        # Assuming entry['parts'] is a list of dictionaries, and we need the 'text' from the first one.
        # Adjust if the structure of 'parts' is different.
        if entry.get('parts') and isinstance(entry['parts'], list) and len(entry['parts']) > 0 and 'text' in entry['parts'][0]:
            system_prompt += f"{entry['role']}: {entry['parts'][0]['text']}\\n"
        else:
            # Handle cases where 'parts' might be missing or not in the expected format
            system_prompt += f"{entry['role']}: [message content not available in expected format]\\n"


    model_with_system_prompt = genai.GenerativeModel(
        'gemini-2.5-flash-preview-04-17', # Corrected model name
        system_instruction=genai.types.ContentDict(parts=[genai.types.PartDict(text=system_prompt)]) # More explicit
    )

    api_chat_history: List[Dict[str, Any]] = []
    for entry in conversation_history:
        # Ensure parts are correctly formatted for the API
        parts_for_api = []
        if isinstance(entry.get('parts'), list):
            for part_item in entry['parts']:
                if isinstance(part_item, dict) and 'text' in part_item:
                    parts_for_api.append(part_item['text'])
                elif isinstance(part_item, str): # If parts are already strings
                    parts_for_api.append(part_item)
        api_chat_history.append({'role': entry['role'], 'parts': parts_for_api})


    try:
        chat = model_with_system_prompt.start_chat(history=api_chat_history) # History up to the last user message
        response = chat.send_message(user_query)

        ai_response_text: str = response.text
        conversation_history.append({"role": "user", "parts": [{"text": user_query}]})
        conversation_history.append({"role": "model", "parts": [{"text": ai_response_text}]})
        save_user_profile()
        return ai_response_text
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return "I'm sorry, I encountered an error trying to process your request."


# --- Main CLI Loop ---
def main() -> None:
    print("Welcome to Agent-G (CLI Mode)!")
    print("Your AI assistant for Richard Stephen's notebooks.")

    load_user_profile(DEFAULT_USER_PROFILE)
    if not current_user_profile:
        print("Could not load or create a user profile. Exiting.")
        return

    load_transcriptions()
    if not notebook_data: # Check after loading
        print("No notebook data loaded. The agent may not have any information to work with. Exiting.")
        # It might be better to allow the program to continue if the user profile loaded,
        # as the user might want to chat without notebook context or load it later.
        # For now, keeping original behavior.
        return

    print(f"\nHello {current_user_profile.get('preferred_name', 'User')}! How can I help you today?")
    print("Type 'exit' or 'quit' to end the conversation.")

    while True:
        user_input: str = input("> ").strip()
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            save_user_profile()
            break

        if not user_input:
            continue

        ai_response: str = get_gemini_response(user_input)
        print(f"Agent-G: {ai_response}")

if __name__ == "__main__":
    main()

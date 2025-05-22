import os
from typing import Optional
from . import config
from . import data_manager
from . import llm_service

# --- System Prompt Loading Function ---
def load_system_prompt_base(filepath: str) -> Optional[str]:
    """Loads the base system prompt from a specified markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: System prompt file not found at {filepath}. Cannot proceed.")
        return None 
    except Exception as e:
        print(f"Error reading system prompt file {filepath}: {e}. Cannot proceed.")
        return None

# --- Main CLI Loop ---
def main() -> None:
    print("Welcome to Agent-G (CLI Mode)!")
    print("Your AI assistant")

    # 0. Load System Prompt Base first
    system_prompt_base = load_system_prompt_base(config.SYSTEM_PROMPT_FILE_PATH)
    if system_prompt_base is None: # Check if loading failed
        print("Exiting due to system prompt loading error.")
        return

    # 1. Configure API
    config.configure_gemini_api()

    # 2. Load user profile
    if not data_manager.load_user_profile(config.USER_PROFILE_DIR, config.DEFAULT_USER_PROFILE_FILENAME):
        print("Continuing with a default or error-state user profile.")
    
    current_user = data_manager.get_current_user()
    if not current_user:
        print("Critical Error: No user profile loaded (not even default). Exiting.")
        return

    # 3. Load transcriptions
    if not data_manager.load_transcriptions(config.TRANSCRIPTION_DIR):
        print("No notebook data loaded. The agent may not have any information to work with.")

    print(f"\nHello {current_user.get('preferred_name', 'User')}! How can I help you today?")
    print("Type 'exit' or 'quit' to end the conversation.")

    while True:
        user_input: str = input("> ").strip()
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            # Save history on exit using the currently loaded default profile filename
            data_manager.save_user_profile(config.USER_PROFILE_DIR, config.DEFAULT_USER_PROFILE_FILENAME)
            break

        if not user_input:
            continue

        # 4. Get LLM response
        ai_response: str = llm_service.get_gemini_response(
            user_query=user_input,
            system_prompt_base=system_prompt_base, # Use the loaded prompt
            current_user=data_manager.get_current_user(), # Pass the current user object
            conversation_history=data_manager.get_conversation_history(),
            full_transcribed_text=data_manager.get_full_transcribed_text(),
            model_name=config.GEMINI_MODEL_NAME
        )
        
        print(f"Agent-G: {ai_response}")

        # 5. Update conversation history (locally in data_manager's state)
        data_manager.add_to_conversation_history(role="user", text=user_input)
        data_manager.add_to_conversation_history(role="model", text=ai_response)
        
        # 6. Save profile (includes updated history) after each interaction
        data_manager.save_user_profile(config.USER_PROFILE_DIR, config.DEFAULT_USER_PROFILE_FILENAME)


if __name__ == "__main__":
    main()

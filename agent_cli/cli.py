from typing import Optional
from . import config
from . import data_manager
from . import llm_service

# --- Main CLI Loop ---
def main() -> None:
    """Runs the main command-line interface loop for Agent-G.

    This function initialises the application, loads necessary configurations
    and data, then enters a loop to interact with the user. It processes
    user input, gets responses from the LLM, and manages conversation
    history.
    """
    print("Welcome to Agent-G (CLI Mode)!")
    print("Your AI assistant")

    # Load and decrypt system prompt using data_manager
    if not data_manager.load_and_decrypt_system_prompt(config.SYSTEM_PROMPT_FILE_PATH):
        print("Exiting due to system prompt loading error.")
        return
    
    system_prompt_base: Optional[str] = data_manager.get_decrypted_system_prompt()
    if system_prompt_base is None: # Should be redundant if load_and_decrypt_system_prompt handles exit
        print("Critical Error: System prompt not available after loading attempt. Exiting.")
        return

    config.configure_gemini_api()

    if not data_manager.load_user_profile(config.USER_PROFILE_DIR, config.DEFAULT_USER_PROFILE_FILENAME):
        print("Continuing with a default or error-state user profile.")
    
    current_user: Optional[dict] = data_manager.get_current_user()
    if not current_user:
        print("Critical Error: No user profile loaded (not even default). Exiting.")
        return

    if not data_manager.load_transcriptions(config.TRANSCRIPTION_DIR):
        print("No notebook data loaded. The agent may not have any information to work with.")

    print(f"\nHello {current_user.get('preferred_name', 'User')}! How can I help you today?")
    print("Type 'exit' or 'quit' to end the conversation.")

    while True:
        user_input: str = input("> ").strip()
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            data_manager.save_user_profile(config.USER_PROFILE_DIR, config.DEFAULT_USER_PROFILE_FILENAME)
            break

        if not user_input:
            continue

        ai_response: str = llm_service.get_gemini_response(
            user_query=user_input,
            current_user=data_manager.get_current_user(), 
            conversation_history=data_manager.get_conversation_history(),
            full_transcribed_text=data_manager.get_full_transcribed_text(),
            model_name=config.GEMINI_MODEL_NAME
        )
        
        print(f"Agent-G: {ai_response}")

        data_manager.add_to_conversation_history(role="user", text=user_input)
        data_manager.add_to_conversation_history(role="model", text=ai_response)
        
        data_manager.save_user_profile(config.USER_PROFILE_DIR, config.DEFAULT_USER_PROFILE_FILENAME)


if __name__ == "__main__":
    main()

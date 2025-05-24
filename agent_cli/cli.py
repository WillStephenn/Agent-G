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

    # --- User Profile Selection ---
    available_profiles = data_manager.list_available_profiles(config.USER_PROFILE_DIR)
    selected_profile_filename = config.DEFAULT_USER_PROFILE_FILENAME # Default

    if available_profiles:
        print("\nAvailable user profiles:")
        profile_map = {} # Maps display number to actual filename
        
        displayable_profiles = [] # Profiles other than current default for numbered list
        default_profile_exists_in_list = any(p == config.DEFAULT_USER_PROFILE_FILENAME for p in available_profiles)

        idx = 1
        for profile_name in sorted(available_profiles): # Sort for consistent ordering
            if profile_name == config.DEFAULT_USER_PROFILE_FILENAME and default_profile_exists_in_list:
                continue # Will be offered as option 0 or default Enter action
            display_name = profile_name.replace(".json.enc", "")
            print(f"  {idx}. {display_name}")
            profile_map[str(idx)] = profile_name
            idx += 1
        
        default_display_name = config.DEFAULT_USER_PROFILE_FILENAME.replace(".json.enc", "")
        if default_profile_exists_in_list:
            print(f"  0. Use current default: {default_display_name}")
        else:
            print(f"  0. Create/use default named: {default_display_name}")
        # Option 0 always maps to the configured default filename
        profile_map["0"] = config.DEFAULT_USER_PROFILE_FILENAME
        
        prompt_message = f"Select profile by number, type new name, or press Enter for default ({default_display_name}): "
        
        while True:
            choice_input = input(prompt_message).strip()
            
            if not choice_input: # Enter for default
                selected_profile_filename = config.DEFAULT_USER_PROFILE_FILENAME
                print(f"Using default profile: {selected_profile_filename.replace('.json.enc', '')}")
                break
            elif choice_input in profile_map:
                selected_profile_filename = profile_map[choice_input]
                print(f"Selected profile: {selected_profile_filename.replace('.json.enc', '')}")
                break
            else: # Potentially a new profile name
                if choice_input and all(c.isalnum() or c in ('_', '-') for c in choice_input) and not choice_input.startswith('.') and choice_input not in [".", ".."]:
                    selected_profile_filename = f"{choice_input}.json.enc"
                    print(f"Using new/selected profile: {choice_input}")
                    break
                else:
                    print("Invalid input. Please enter a number from the list, a valid new profile name (alphanumeric, _, -), or press Enter.")
    else:
        print(f"\nNo existing user profiles found in '{config.USER_PROFILE_DIR}'.")
        default_display_name = config.DEFAULT_USER_PROFILE_FILENAME.replace(".json.enc", "")
        prompt_message = f"Enter a name for the new profile, or press Enter to use default '{default_display_name}': "
        
        while True:
            choice_input = input(prompt_message).strip()
            if not choice_input:
                selected_profile_filename = config.DEFAULT_USER_PROFILE_FILENAME
                print(f"Using default profile name: {selected_profile_filename.replace('.json.enc', '')}")
                break
            elif choice_input and all(c.isalnum() or c in ('_', '-') for c in choice_input) and not choice_input.startswith('.') and choice_input not in [".", ".."]:
                selected_profile_filename = f"{choice_input}.json.enc"
                print(f"Using new profile name: {choice_input}")
                break
            else:
                print("Invalid profile name. Please use alphanumeric characters, underscores, or hyphens, or press Enter for default.")

    # Load the selected or default user profile
    if not data_manager.load_user_profile(config.USER_PROFILE_DIR, selected_profile_filename):
        # data_manager.load_user_profile now prints more specific messages.
        # This print might be redundant or could state that a fallback in-memory profile is active.
        print(f"Note: There was an issue loading '{selected_profile_filename}'. A new or fallback profile state is active.")
    
    current_user: Optional[dict] = data_manager.get_current_user()
    if not current_user: # Should be handled by load_user_profile ensuring _current_user_profile is set
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
            data_manager.save_user_profile(config.USER_PROFILE_DIR, selected_profile_filename)
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
        
        data_manager.save_user_profile(config.USER_PROFILE_DIR, selected_profile_filename)


if __name__ == "__main__":
    main()

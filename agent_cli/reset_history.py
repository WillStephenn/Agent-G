import os
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_PROFILE_DIR = os.path.join(SCRIPT_DIR, "../user_profiles/")

def reset_conversation_history(profile_filename: str):
    """Loads a user profile, clears its conversation history, and saves it."""
    profile_path = os.path.join(USER_PROFILE_DIR, profile_filename)

    if not os.path.exists(profile_path):
        print(f"Error: User profile not found: {profile_path}")
        return

    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            user_profile = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from profile: {profile_path}")
        return
    except Exception as e:
        print(f"Error reading user profile {profile_filename}: {e}")
        return

    if "conversation_history" not in user_profile:
        print(f"Warning: 'conversation_history' not found in {profile_filename}. Nothing to reset.")
        # Optionally, create it if it doesn't exist
        # user_profile["conversation_history"] = [] 
    else:
        user_profile["conversation_history"] = []
        print(f"Conversation history cleared for {profile_filename}.")

    try:
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(user_profile, f, indent=2)
        print(f"User profile saved: {profile_path}")
    except Exception as e:
        print(f"Error saving user profile {profile_filename}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Reset conversation history for a user profile.")
    parser.add_argument("profile_filename", 
                        help="The filename of the user profile (e.g., isobel_stephen.json)")
    
    args = parser.parse_args()

    if not args.profile_filename.endswith(".json"):
        print("Error: Profile filename must end with .json")
        print("Example usage: python reset_history.py isobel_stephen.json")
        return

    reset_conversation_history(args.profile_filename)

if __name__ == "__main__":
    main()

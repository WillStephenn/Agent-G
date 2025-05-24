import google.generativeai as genai
from typing import List, Dict, Any, Optional
from . import data_manager

def get_gemini_response(
    user_query: str,
    current_user: Optional[Dict[str, Any]],
    conversation_history: List[Dict[str, Any]],
    full_transcribed_text: str,
    model_name: str
) -> str:
    """Constructs the full prompt and gets a response from the Gemini API.

    Args:
        user_query (str): The user's current query or message.
        current_user (Optional[Dict[str, Any]]): A dictionary containing the current user's profile information,
            including 'preferred_name', 'pronouns', and 'context'. Can be None if no user is loaded.
        conversation_history (List[Dict[str, Any]]): A list of past messages in the conversation,
            where each message is a dictionary with 'role' and 'parts'.
        full_transcribed_text (str): The full transcribed text from the user's notebook or input source.
        model_name (str): The name of the Gemini model to use (e.g., "gemini-pro").

    Returns:
        str: The AI's response as a string, or an error message if an issue occurs.
    """
    if current_user is None:
        return "Error: User profile not loaded for LLM service."

    system_prompt_base = data_manager.get_decrypted_system_prompt()
    if system_prompt_base is None:
        return "Error: Could not load or decrypt the system prompt for LLM service."

    user_specific_prompt = f"The user you are currently assisting is {current_user.get('preferred_name', 'the user')}. Address them by this name.\n"
    user_specific_prompt += f"Their pronouns are {current_user.get('pronouns', 'they/them')}.\n"
    
    user_context = current_user.get("context", "")
    if user_context:
        user_specific_prompt += f"\nSome background context about this user: {user_context}\n\n"
    else:
        user_specific_prompt += "\n"

    full_system_prompt = (
        f"{system_prompt_base}\n"
        f"{user_specific_prompt}"
        f"The transcribed notebook content is provided below:\n{full_transcribed_text}\n\n"
        f"Conversation History:\n"
    )

    api_chat_history: List[Dict[str, Any]] = []
    for entry in conversation_history:
        parts_for_api = []
        if isinstance(entry.get('parts'), list):
            for part_item in entry['parts']:
                if isinstance(part_item, dict) and 'text' in part_item:
                    parts_for_api.append(part_item['text'])
                elif isinstance(part_item, str):
                    parts_for_api.append(part_item)
        api_chat_history.append({'role': entry['role'], 'parts': parts_for_api})
    
    system_instruction_content = genai.types.ContentDict(
        parts=[genai.types.PartDict(text=full_system_prompt)]
    )

    try:
        model = genai.GenerativeModel(
            model_name,
            system_instruction=system_instruction_content
        )
        
        chat = model.start_chat(history=api_chat_history)
        response = chat.send_message(user_query)
        
        ai_response_text: str = response.text
        return ai_response_text
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return "I'm sorry, I encountered an error trying to process your request."


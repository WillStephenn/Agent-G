import google.generativeai as genai
from typing import List, Dict, Any, Optional

def get_gemini_response(
    user_query: str,
    system_prompt_base: str, # The static part of the system prompt
    current_user: Optional[Dict[str, Any]],
    conversation_history: List[Dict[str, Any]],
    full_transcribed_text: str,
    model_name: str
) -> str:
    """
    Constructs the full prompt and gets a response from the Gemini API.
    """
    if current_user is None:
        return "Error: User profile not loaded for LLM service."

    # Construct the dynamic parts of the system prompt
    user_specific_prompt = f"The user you are currently assisting is {current_user.get('preferred_name', 'the user')}. Address them by this name.\n"
    user_specific_prompt += f"Their pronouns are {current_user.get('pronouns', 'they/them')}.\n"
    
    user_context = current_user.get("context", "")
    if user_context:
        user_specific_prompt += f"\nSome background context about this user: {user_context}\n\n"
    else:
        user_specific_prompt += "\n"

    # Combine static base, user specifics, transcribed text, and critical instructions
    # The critical instructions are part of the system_prompt_base
    full_system_prompt = (
        f"{system_prompt_base}\n"
        f"{user_specific_prompt}"
        f"The transcribed notebook content is provided below:\n{full_transcribed_text}\n\n"
        f"Conversation History:\n"
    )

    # Prepare history for the API call (system prompt + actual history)
    # The Gemini API's `start_chat` can take a `system_instruction` and then `history`.
    # The `system_instruction` should be the complete guiding prompt.
    # The `history` should be the actual user/model turn-by-turn.

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
    
    # The system prompt itself
    system_instruction_content = genai.types.ContentDict(
        parts=[genai.types.PartDict(text=full_system_prompt)]
    )

    try:
        model = genai.GenerativeModel(
            model_name,
            system_instruction=system_instruction_content
        )
        
        chat = model.start_chat(history=api_chat_history) # Pass only actual conversation turns
        response = chat.send_message(user_query)
        
        ai_response_text: str = response.text
        return ai_response_text
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        # Log the full prompt and history for debugging if needed, being mindful of sensitive data
        # print(f"DEBUG: Failing System Prompt: {full_system_prompt}")
        # print(f"DEBUG: Failing History: {api_chat_history}")
        # print(f"DEBUG: User Query: {user_query}")
        return "I'm sorry, I encountered an error trying to process your request."


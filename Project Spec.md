# Project Grandma's Helper: AI Notebook Navigator

**Version:** 1.0
**Date:** May 16, 2025
**Author:** William Stephen

## 1. Project Goal

To create a WhatsApp-based AI assistant that helps Grandma navigate and understand the content of Grandpa's notebooks. The assistant will provide information, guidance on how things work, and support for accessing online information, all in an empathetic and easy-to-understand manner. A key priority is ensuring the privacy and security of sensitive information.

## 2. Core Features

### 2.1. Handwriting Transcription
* **Input:** Photos of handwritten pages from Grandpa's notebooks. 
* **Process:** Utilize the Gemini API to perform Optical Character Recognition (OCR) and transcribe the handwriting into digital text.
* **Output:** Plain text files for each notebook page, stored locally for processing.
* **Notes** The source will be the ./pictures directory. The notebooks will be pre-processed once in order to instansiate the agent. 

### 2.2. Conversational AI Agent
* **Engine:** Gemini API.
* **Personality & Tone:**
    * Kind, patient, and empathetic.
    * Supportive and positive outlook.
    * Explains technical or complex topics in simple, step-by-step, jargon-free language.
    * Addresses Grandma respectfully (e.g., by her preferred name, if configured).
    * Keeps responses super concise and friendly like a person texting - brief, conversational messages rather than lengthy explanations.
* **Context:** The agent will use the transcribed text from the notebooks as its primary knowledge base.
        
* **Capabilities:**
    * Answer questions based on the notebook content.
    * Help Grandma understand instructions left by Grandpa.
    * Provide guidance on navigating online administrative tasks (in a general, guiding way).
    * The agent should be able to generalise to other users in the family who want to. There will need to be some way to retrieve who on the phone number whitelist is messaging, so it knows how to address them and can load up the conversation context. 



### 2.3. Information Retrieval (Non-Sensitive)
* The agent will directly answer questions and provide information from the notebooks when the information is non-sensitive.

### 2.4. Sensitive Information Handling (IRL Lookup)
* **Strategy:** To ensure maximum privacy, sensitive information (e.g., passwords, bank details, PINs) will *never* be digitized.
* **Process:**
    1. During notebook preparation, all sensitive information will be physically covered with paper notes indicating where the real information can be found (e.g., "Blue Notebook, page 5").
    2. Only these covered pages will be photographed, ensuring sensitive data is never digitized.
    3. The AI will recognize these reference markers and provide the proper lookup locations.
    * *Example User Query:* "What's the password for the electricity account?"
    * *Example AI Response:* "You can find the password for the electricity account in Grandpa's Red Notebook on page 12."

### 2.5. User Interface
* **Platform:** WhatsApp.
* **Interaction:** Grandma will interact with the AI by sending text messages to a dedicated WhatsApp number.

## 3. Technical Stack

* **Programming Language:** Python (Version 3.x)
* **AI Services:**
    * **Google Gemini API:**
        * For handwriting transcription (processing images of notebook pages).
        * For the conversational AI engine.
        * An API key will be set up for this project.
* **Security & Encryption:**
    * **Data Encryption:**
        * All sensitive information will be stored in encrypted files, including:
            * Phone number whitelists
            * User profiles and preferences for family members
            * Conversation logs and history
            * System prompts and configurations
        * No sensitive data will be hardcoded in the application.
    * **Key Python Libraries for Security:**
        * `cryptography`: For encryption/decryption of sensitive data files
        * `pydantic`: For secure configuration management
        * `keyring`: For secure storage of encryption keys
* **WhatsApp Integration:**
    * **Twilio API for WhatsApp:**
        * To send and receive messages.
        * Leveraging Twilio's free tier (first 1,000 conversations per month free, as of current understanding).
* **Hosting (Python Backend):**
    * **Provider:** PythonAnywhere (Recommended for its ease of setup, free tier for a basic web app, and Python focus).
    * **Alternative Free Tiers to Consider:** Google Cloud Functions, AWS Lambda (these are serverless and very cost-effective but might have a slightly different setup paradigm than a persistent web app on PythonAnywhere).
    * **Requirements:** The hosting will run a Python web application (e.g., using Flask) to act as a webhook for Twilio, process incoming messages, interact with the Gemini API, and formulate responses.
* **Key Python Libraries/Frameworks:**
    * `twilio`: To interact with the Twilio API.
    * `google-generativeai`: To interact with the Gemini API.
    * `Flask` (or `FastAPI`): To create the web application and webhook endpoint. Flask is generally very beginner-friendly for this scale.
    * `requests`: For making HTTP requests if needed (often bundled or a dependency).
    * `python-dotenv`: For managing environment variables (like API keys) locally during development.

## 4. Security Measures

* **Sensitive Data Handling:** As per section 2.4, sensitive data will not be digitized or accessible by the AI. The AI will only provide pointers to physical locations in notebooks.
* **WhatsApp Bot Access Control:**
    * **Phone Number Whitelist:** The Python application will maintain a whitelist of approved phone numbers (Grandma's WhatsApp number, your test number).
    * Only messages from whitelisted numbers will be processed. Messages from unknown numbers will be ignored (no response sent back to avoid confirming the number is active).
    * The sender's phone number will be retrieved from the incoming Twilio webhook request.
* **API Key Management:**
    * All API keys (Twilio, Gemini) will be stored securely as environment variables on the hosting platform (e.g., PythonAnywhere environment variables) and *not* hardcoded in the script.
* **Webhook Security:**
    * The webhook URL exposed to Twilio will be an HTTPS endpoint.
* **Data Sent to Gemini:** Only non-sensitive, transcribed notebook content and the conversation itself (from the whitelisted number) will be sent to the Gemini API.

## 5. Key Setup Steps (High-Level)

1.  **Grandpa's Notebooks:**
    * Photograph all pages clearly.
    * Manually review photos/transcriptions to identify locations (notebook/page) of sensitive information. This mapping will be implicitly part of the AI's "knowledge" when it's programmed to guide IRL lookups.
2.  **Gemini API Setup:**
    * Obtain a Gemini API key.
    * Write Python scripts to:
        * Upload notebook page images to Gemini for transcription.
        * Store transcribed text.
3.  **Twilio Setup:**
    * Create a Twilio account.
    * Set up the Twilio Sandbox for WhatsApp initially for development, then provision a dedicated Twilio number if desired (may involve costs beyond the free message tier for the number itself).
    * Note Account SID, Auth Token, and Twilio WhatsApp number.
4.  **Python Backend Application (Flask/FastAPI):**
    * Develop the core application logic:
        * Webhook endpoint to receive messages from Twilio.
        * Function to extract sender's number and message body.
        * Implement phone number whitelist check.
        * Function to interact with Gemini API (send context + user query, receive response).
        * Logic to formulate IRL lookup responses for sensitive queries.
        * Function to send responses back via Twilio.
5.  **Hosting Setup (PythonAnywhere - Recommended):**
    * Create a PythonAnywhere account (free tier).
    * Deploy the Python Flask application.
    * Configure environment variables for API keys (Gemini, Twilio).
    * Configure the PythonAnywhere web app to serve your Flask app via HTTPS.
    * Update Twilio webhook settings to point to the live PythonAnywhere URL.
6.  **Testing:**
    * Thoroughly test with your own whitelisted number.
    * Test with Grandma's whitelisted number.
    * Test edge cases and sensitive information queries.

## 6. Future Considerations (Optional)

* **Voice Notes:** Explore allowing Grandma to send WhatsApp voice notes, transcribing them to text before sending to Gemini.
* **Context Updates:** Plan a simple way to update the AI's knowledge base if new non-sensitive information needs to be added.
* **Error Monitoring/Alerting:** For a more robust system, basic error logging or alerting if the bot goes down.
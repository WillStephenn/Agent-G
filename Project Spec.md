# Project Agent-G: AI Notebook Navigator

**Version:** 1.2
**Date:** May 17, 2025
**Author:** William Stephen

## 1. Project Goal

To create a WhatsApp-based AI assistant that help the family navigate and understand the content of notebooks containing information and instructions left behind by Richard Stephen after his passing. The assistant will provide information, guidance on how things work, and support for accessing online information, all in an empathetic and easy-to-understand manner. A key priority is ensuring the privacy and security of sensitive information. The assistant should be provided context about the family member messaging them, and have their conversation history loaded into context. This system needs to be dynamic and grow with time. The first version of this system will be specifically for one user, Isobel Stephen who is his widow, but should have future expansion in mind when features are being built. For example, the assistant should have user profiles loaded into context depending on who on the phone number whitelist messaged them. 

## 2. Core Features

### 2.1. Handwriting Transcription
* **Input:** Transcription of photos of handwritten pages from notebooks. Sensitive information on pages will be physically covered with a slip of paper simply stating "REDACTED" before photography.
* **Process:**
    * Use the Gemini Flash model ("gemini-2.5-flash-preview-04-17") to perform transcriptions from handwriting image to tagged text.
    * **Typo Correction & Original Text Preservation:**
        * The Gemini API will be instructed: "If you encounter obvious spelling errors or typos, please correct them in the main transcription. For each correction made, preserve the original as-transcribed word/phrase immediately after the corrected text, encapsulated within an XML-style tag: `<original_text>original uncorrected text</original_text>`."
        * Example output: "He went to the store `<original_text>stor</original_text>` to buy bread `<original_text> bred </original_text>`."
    * **Redacted Information Handling (During Transcription):**
        * The Gemini API will be instructed: "If you encounter the word 'REDACTED' (transcribed from a physical cover slip in the image), transcribe it, but also encapsulate this specific word 'REDACTED' within an XML-style tag: `<redacted_marker/>`."
        * Example output: "...Password: <redacted_marker/>..."
* **Output & Filename Convention:**
    * Plain text files for each notebook page, including any `<original_text>` and `<redacted_marker/>` tags.
    * **Crucial:** Files will be named using a strict convention to encode their source: `[NotebookIdentifier]___[PageNumber].txt` (e.g., `BlueFinancialNotebook___Page023.txt`, using triple underscores as a clear delimiter and zero-padding page numbers for consistent sorting). This filename is the key to locating IRL information. Information about which notebook it came from will be in the image file name.
* **Notes:** The source image directory will be `./pictures`. Notebooks will be pre-processed once. A post-transcription review step will then occur.

### 2.2. Conversational AI Agent
* **Engine:** Gemini API.
* **Model Selection Strategy:**
    * **Model:** "gemini-2.5-flash-preview-04-17"
* **Personality & Tone:**
    * Kind, patient, and empathetic.
    * Supportive and positive outlook.
    * Explains technical or complex topics in simple, step-by-step, jargon-free language.
    * Addresses users respectfully (e.g., by their preferred name, with preffered pronouns if configured).
    * Keeps responses super concise and friendly like a person texting - brief, conversational messages rather than lengthy explanations.
* **Context Provisioning:**
    * The agent's knowledge base will be a folder containing all of the transcribed text files.
    * This text will form part of the system prompt and the entire contents of the text files will be injected at point of system prompt construction.
    * When a piece of text is loaded into context, the Python backend *must* also provide the `NotebookIdentifier` and `PageNumber` (extracted from the source filename of that text chunk) to the Gemini agent along with the text itself. This metadata is essential for handling IRL lookups.
* **Capabilities:**
    * Answer questions based on the non-sensitive notebook content.
    * Help the user understand instructions from the notebook.
    * Provide guidance on navigating online administrative tasks (in a general, guiding way that is friendly to low tech literacy users).
    * For sensitive information (indicated by `<redacted_marker/>`), guide the user to the physical location in the notebooks using the filename-derived context.
    * Identify the whitelisted family member messaging (based on their phone number) to address them appropriately.

### 2.3. Information Retrieval (Non-Sensitive)
* The agent will directly answer questions and provide information from the notebooks when the information is non-sensitive and does not involve a `<redacted_marker/>` tag.

### 2.4. Sensitive Information Handling (IRL Lookup)
* **Strategy:** To ensure maximum privacy, sensitive information (e.g., passwords, bank details, PINs) will *never* be directly digitised or stated by the AI.
* **Physical Redaction Process (Before Photography):**
    1.  Identify sensitive information in the physical notebooks.
    2.  Physically cover this information with a slip of paper on which only the word "REDACTED" is clearly handwritten.
    3.  Photograph notebook pages with these slips in place.
* **Transcription of Redacted Slips:** The word "REDACTED" from the slip will be transcribed and tagged as `<redacted_marker/>` by the transcription process (see Section 2.1). The filename of the resulting text file (e.g., `RedNotebook___Page012.txt`) holds the location context.
* **Chatbot Response to Sensitive Queries:**
    * The chatbot's system prompt will instruct it: "If the text relevant to answering the users question contains a `<redacted_marker/>` tag, this indicates sensitive information that requires an IRL lookup. DO NOT state that it's redacted or that you cannot provide the information directly. Instead, use the source `NotebookIdentifier` and `PageNumber` associated with that piece of text (which will be provided as part of your context). Politely tell the user where they can find that specific piece of information in the physical notebooks."
    * *Example User Query:* "What's the password for the electricity account?"
    * *Example AI Context (simplified):* Text chunk: "...Password: `<redacted_marker/>`...", Source: `RedNotebook, Page012`.
    * *Example AI Response:* "You can find that password information in Grandpa's Red Notebook on page 12."

### 2.5. User Interface
* **Platform:** WhatsApp.
* **Interaction:** Family members (on the whitelist) will interact with the AI by sending text messages to a dedicated WhatsApp number.

## 3. Technical Stack

* **Programming Language:** Python (Version 3.x)
* **AI Services:**
    * **Google Gemini API:** (Transcription and Conversational AI)
        * Model: "gemini-2.5-flash-preview-04-17"
* **Security & Encryption (Local Data):**
    * Operational data like whitelists, user profiles, system prompts, conversation logs, should be stored as files (and not be contained within the python script) and should be protected.
    * `cryptography` library for file encryption if local storage of these operational files is needed.
    * Encryption keys managed via environment variables on the server.
* **WhatsApp Integration:**
    * **Twilio API for WhatsApp:** (free tier)
* **Hosting (Python Backend):**
    * **Provider:** PythonAnywhere (Recommended).
    * **Requirements:** Python web app (e.g., Flask) for Twilio webhook.
* **Key Python Libraries/Frameworks:**
    * `twilio`, `google-generativeai`, `Flask` (or `FastAPI`), `requests`, `python-dotenv`.
    * `os` (for filename parsing), `re` (for parsing tags if needed).
* **Security Measures:**
* **Sensitive Data Handling:** Notebook sensitive data is never digitised; `<redacted_marker/>` in text + filename context points to physical location.
* **WhatsApp Bot Access Control:** Phone number whitelist enforced. Phone numbers will have names and pronouns associated with them so the agent knows who it is talking to, and their conversation history can be pulled up. 
* **API Key Management:** Securely via environment variables on the hosting platform.
* **Webhook Security:** HTTPS endpoint.
* **Data Sent to Gemini:** Only non-sensitive, transcribed notebook content (with `<redacted_marker/>` tags) and conversation data from whitelisted users. Filename-derived location data is used by the *chatbot* to formulate IRL guidance, and is sent to Gemini as part of the chunk's context. The system prompt should ensure it's used for IRL guidance only.

## 5. Key Setup Steps (High-Level)

1.  **Grandpa's Notebooks Preparation:**
    * Identify sensitive info in physical notebooks.
    * Cover sensitive info with slips of paper, each clearly handwritten with "REDACTED".
    * Photograph all notebook pages. Name image files systematically (e.g., `BlueNotebook_Page023.jpg`).
2.  **Gemini API Setup (Transcription):**
    * Obtain Gemini API key.
    * Develop Python script to:
        * Iterate through images.
        * Send images to Gemini with transcription prompt (handling typos/originals and `<redacted_marker/>` for "REDACTED").
        * Save transcribed text to files named `[NotebookIdentifier]___[PageNumber].txt` based on the source image's name or manual logging.
    * **Review Transcriptions:** Check `<original_text>` tags and ensure `<redacted_marker/>` tags are correctly placed.
3.  **Twilio Setup:**
    * Create a Twilio account.
    * Set up the Twilio Sandbox for WhatsApp initially for development, then provision a dedicated Twilio number if desired (may involve costs beyond the free message tier for the number itself).
    * Note Account SID, Auth Token, and Twilio WhatsApp number.
4.  **Python Backend Application (Flask/FastAPI):**
    * Develop core logic:
        * Webhook for Twilio.
        * Whitelist check using sender's `From` number.
        * Logic to retrieve relevant transcribed text chunks. **Crucially, when retrieving text for context, also retrieve/construct its `NotebookIdentifier` and `PageNumber` from its filename.**
        * Pass text chunk *and its source (notebook, page)* to Gemini for conversational response, using the system prompt that explains handling `<redacted_marker/>` by referring to the provided source.
        * Send responses via Twilio.
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

* **Voice Notes:** Explore allowing users to send WhatsApp voice notes, transcribing them to text before sending to Gemini.
* **Context Updates:** Plan a simple way to update the AI's knowledge base if new non-sensitive information needs to be added.
* **Error Monitoring/Alerting:** For a more robust system, basic error logging or alerting if the bot goes down.
# Project Agent-G: AI Notebook Navigator

**Version:** 1.3
**Date:** May 17, 2025
**Author:** William Stephen

## 1. Project Goal

To create a WhatsApp-based AI assistant that help the family navigate and understand the content of notebooks containing information and instructions left behind by Richard Stephen after his passing. The assistant will provide information, guidance on how things work, and support for accessing online information, all in an empathetic and easy-to-understand manner. A key priority is ensuring the privacy and security of sensitive information. The assistant should be provided context about the family member messaging them, and have their conversation history loaded into context. This system needs to be dynamic and grow with time. The first version of this system will be specifically for one user, Isobel Stephen who is his widow, but should have future expansion in mind when features are being built. For example, the assistant should have user profiles loaded into context depending on who on the phone number whitelist messaged them. 

## 2. Core Features

### 2.1. Handwriting Transcription
* **Input:** Transcription of photos of handwritten pages from notebooks, sourced from the `./pictures/` directory. Sensitive information on pages will be physically covered with a slip of paper simply stating "REDACTED" before photography.
* **Process (Initial Transcription):**
    * The `transcription_service/transcribe.py` script will use the Gemini Flash model ("gemini-2.5-flash-preview-04-17") to perform transcriptions from handwriting image to tagged text.
    * **Typo Correction & Original Text Preservation:**
        * The Gemini API will be instructed: "If you encounter obvious spelling errors or typos, please correct them in the main transcription. For each correction made, preserve the original as-transcribed word/phrase immediately after the corrected text, encapsulated within an XML-style tag: `<original_text>original uncorrected text</original_text>`."
        * Example output: "He went to the store `<original_text>stor</original_text>` to buy bread `<original_text> bred </original_text>`."
    * **Redacted Information Handling (During Transcription):**
        * The Gemini API will be instructed: "If you encounter the word 'REDACTED' (transcribed from a physical cover slip in the image), transcribe it, but also encapsulate this specific word 'REDACTED' within an XML-style tag: `<redacted_marker/>`."
        * Example output: "...Password: <redacted_marker/>..."
* **Output & Filename Convention (Initial Transcription):**
    * Plain text files for each notebook page, including any `<original_text>` and `<redacted_marker/>` tags.
    * Files will be saved to the `transcription_service/raw_transcriptions/` directory.
    * **Crucial:** Files will be named using a strict convention to encode their source: `[NotebookIdentifier]___[PageNumber].txt` (e.g., `BlueFinancialNotebook___Page023.txt`, using triple underscores as a clear delimiter and zero-padding page numbers for consistent sorting). This filename is the key to locating IRL information. Information about which notebook it came from will be in the image file name.
* **Notes:** Notebooks will be pre-processed once. A post-transcription review step will then occur on these plain text files in `transcription_service/raw_transcriptions/`.

### 2.1.1. Context Preparation and Encryption
* **Purpose:** To prepare the transcribed notebook pages for secure use by the AI agent.
* **Process:**
    * A dedicated script, `utilities/prepare_context.py`, will be run after the initial transcription and review.
    * This script will:
        1. Read each plain text transcription file from the `transcription_service/raw_transcriptions/` directory.
        2. Encrypt the content of each file using the project's defined encryption mechanism (see Section 4 - `cryptography` library and environment variable for key, primarily via `agent_cli/encryption_service.py`).
        3. Save the encrypted content to a new file within the `agent_cli` project, specifically in a directory named `agent_cli/notebook_context/`.
        4. The encrypted files will retain the original base filename but will have an added extension to denote encryption, e.g., `[NotebookIdentifier]___[PageNumber].txt.enc`.
* **Output:** Encrypted text files (e.g., `BlueFinancialNotebook___Page023.txt.enc`) located in `agent_cli/notebook_context/`.

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
    * The agent's knowledge base will be the folder `agent_cli/notebook_context/` containing all the encrypted transcribed text files.
    * The system prompt will be loaded from an encrypted file, `agent_cli/system_prompt.md.enc`.
    * The Python backend of the agent (primarily `agent_cli/data_manager.py` and `agent_cli/llm_service.py`) will be responsible for:
        * Loading and decrypting the system prompt from `agent_cli/system_prompt.md.enc`.
        * Listing files in `agent_cli/notebook_context/`.
        * Reading the encrypted content of each relevant file.
        * Decrypting the content in memory (using `agent_cli/encryption_service.py`).
        * This decrypted text will form part of the system prompt, with the entire contents of the relevant decrypted text files being injected at the point of system prompt construction.
    * When a piece of text is loaded and decrypted for context, the Python backend *must* also provide the `NotebookIdentifier` and `PageNumber` (extracted from the source filename of that text chunk, by stripping the `.enc` extension) to the Gemini agent along with the text itself. This metadata is essential for handling IRL lookups.
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
* **Interaction:** Family members (on the whitelist) will interact with the AI by sending text messages to a dedicated WhatsApp number. User profiles and conversation history will be managed as encrypted JSON files in `agent_cli/user_profiles/`.

## 3. Project Directory Structure

The project will adhere to the following directory structure to maintain clarity and separation of concerns:

```
/Agent G/
|-- Project Spec.md
|-- .gitignore
|
|-- agent_cli/                # Core conversational agent application
|   |-- __init__.py
|   |-- cli.py                # Main CLI entry point for the agent
|   |-- config.py             # Agent configuration, .env loading
|   |-- llm_service.py        # Interacts with Gemini API for conversations
|   |-- data_manager.py       # Loads/saves/manages agent's data
|   |-- encryption_service.py # Handles encryption/decryption logic
|   |-- system_prompt.md.enc  # ENCRYPTED system prompt for the agent
|   |-- notebook_context/     # ENCRYPTED notebook transcriptions
|   |-- user_profiles/        # ENCRYPTED user profiles & conversation history
|   |-- .env                  # Agent-specific env vars (API keys, ENCRYPTION_KEY)
|   |-- requirements.txt      # Python dependencies for agent_cli
|
|-- transcription_service/    # Initial handwriting transcription processing
|   |-- __init__.py
|   |-- transcribe.py         # Script for initial handwriting transcription
|   |-- raw_transcriptions/   # PLAIN TEXT output from transcribe.py
|   |-- requirements.txt      # Python dependencies for transcription_service
|   |-- .env                  # (Optional) Transcription service specific env vars
|
|-- pictures/                 # Source images of notebook pages for transcription
|
|-- utilities/                # Shared utility scripts and modules
|   |-- __init__.py
|   |-- prepare_context.py    # Script to encrypt raw_transcriptions to agent_cli/notebook_context/
|
|-- dev_tools/                # Tools for development and maintenance
|   |-- admin_interface/      # Development Admin UI (Locally hosted Web Application)
|   |   |-- __init__.py
|   |   |-- app.py            # (e.g., Flask/Streamlit app for the admin UI)
|   |   |-- templates/        # (If web-based admin UI)
|   |   |-- static/           # (If web-based admin UI)
|   |   |-- requirements.txt  # Python dependencies for the admin UI
|   |   |-- .env              # (Optional) Admin UI specific config
|
|-- tests/                    # (Recommended for future) Unit/integration tests
    |-- test_agent_cli/
    |-- test_transcription_service/
    |-- test_utilities/
```

## 4. Technical Stack

* **Programming Language:** Python (Version 3.x)
* **AI Services:**
    * **Google Gemini API:** (Transcription and Conversational AI)
        * Model: "gemini-2.5-flash-preview-04-17"
* **Security & Encryption (Local Data):**
    * Operational data (the system prompt in `agent_cli/system_prompt.md.enc`, transcribed notebooks in `agent_cli/notebook_context/`, user profiles and conversation logs in `agent_cli/user_profiles/`) should be stored as encrypted files.
    * `cryptography` library for file encryption (via `agent_cli/encryption_service.py`).
    * Encryption keys managed via environment variables (`ENCRYPTION_KEY` in `agent_cli/.env`).
* **WhatsApp Integration:**
    * **Twilio API for WhatsApp:** (free tier)
* **Hosting (Python Backend):**
    * **Provider:** PythonAnywhere (Recommended).
    * **Requirements:** Python web app (e.g., Flask) for Twilio webhook.
* **Key Python Libraries/Frameworks:**
    * `twilio`, `google-generativeai`, `Flask` (or `FastAPI` for `agent_cli` webhook), `requests`, `python-dotenv`, `cryptography`.
    * `Streamlit` or `Flask` for the `dev_tools/admin_interface`.
* **Security Measures:**
* **Sensitive Data Handling:** Notebook sensitive data is never digitised; `<redacted_marker/>` in text + filename context points to physical location. All stored notebook context and user profile data will be encrypted at rest.
* **WhatsApp Bot Access Control:** Phone number whitelist enforced. Phone numbers will have names and pronouns associated with them (stored in encrypted user profiles in `agent_cli/user_profiles/`) so the agent knows who it is talking to, and their conversation history can be pulled up.
* **API Key Management:** Securely via environment variables in `agent_cli/.env`.
* **Webhook Security:** HTTPS endpoint.
* **Data Sent to Gemini:** Only non-sensitive, transcribed notebook content (with `<redacted_marker/>` tags) and conversation data from whitelisted users. Filename-derived location data is used by the *chatbot* to formulate IRL guidance, and is sent to Gemini as part of the chunk's context. The system prompt should ensure it's used for IRL guidance only.

## 5. Key Setup Steps (High-Level)

1.  **Grandpa's Notebooks Preparation:**
    * Identify sensitive info in physical notebooks.
    * Cover sensitive info with slips of paper, each clearly handwritten with "REDACTED".
    * Photograph all notebook pages. Store images in the `./pictures/` directory. Name image files systematically (e.g., `BlueNotebook_Page023.jpg`).
2.  **Gemini API Setup & Initial Transcription:**
    * Obtain Gemini API key (store in `agent_cli/.env`).
    * Develop/use the Python script `transcription_service/transcribe.py` to:
        * Iterate through images in `./pictures/`.
        * Send images to Gemini with transcription prompt (handling typos/originals and `<redacted_marker/>` for "REDACTED").
        * Save transcribed *plain text* to files named `[NotebookIdentifier]___[PageNumber].txt` into the `transcription_service/raw_transcriptions/` directory.
    * **Review Transcriptions:** Manually review the plain text files in `transcription_service/raw_transcriptions/`. Check `<original_text>` tags and ensure `<redacted_marker/>` tags are correctly placed.
3.  **Context Preparation & Encryption:**
    * Ensure `ENCRYPTION_KEY` is set in `agent_cli/.env`.
    * Create an initial `system_prompt.md` (plain text). This can then be encrypted using the Development Admin Interface (see Section 7) or a utility script to create `agent_cli/system_prompt.md.enc`.
    * Run the `utilities/prepare_context.py` script to:
        * Read plain text files from `transcription_service/raw_transcriptions/`.
        * Encrypt their content (using logic from `agent_cli/encryption_service.py`).
        * Save the encrypted files (e.g., `[NotebookIdentifier]___[PageNumber].txt.enc`) to the `agent_cli/notebook_context/` directory.
4.  **Twilio Setup:**
    * Create a Twilio account.
    * Set up the Twilio Sandbox for WhatsApp initially for development, then provision a dedicated Twilio number if desired (may involve costs beyond the free message tier for the number itself).
    * Note Account SID, Auth Token, and Twilio WhatsApp number.
5.  **Python Backend Application (`agent_cli`):**
    * Develop core logic in `agent_cli/` (e.g., `cli.py`, `data_manager.py`, `llm_service.py`):
        * Webhook for Twilio (if using Flask/FastAPI within `agent_cli`).
        * Whitelist check using sender's `From` number (data from encrypted user profiles in `agent_cli/user_profiles/`).
        * Logic to retrieve relevant encrypted text chunks from `agent_cli/notebook_context/`.
        * **Crucially, when retrieving text for context, decrypt it in memory (using `agent_cli/encryption_service.py`) and also retrieve/construct its `NotebookIdentifier` and `PageNumber` from its filename (after stripping `.enc`).**
        * Pass decrypted text chunk *and its source (notebook, page)* to Gemini for conversational response, using the system prompt that explains handling `<redacted_marker/>` by referring to the provided source.
        * Manage and save conversation history to encrypted user profiles in `agent_cli/user_profiles/`.
        * Send responses via Twilio.
6.  **Hosting Setup (PythonAnywhere - Recommended for `agent_cli`):**
    * Create a PythonAnywhere account (free tier).
    * Deploy the Python Flask application from `agent_cli`.
    * Configure environment variables for API keys (Gemini, Twilio) and `ENCRYPTION_KEY` (from `agent_cli/.env`).
    * Configure the PythonAnywhere web app to serve your Flask app via HTTPS.
    * Update Twilio webhook settings to point to the live PythonAnywhere URL.
7.  **Testing:**
    * Thoroughly test with your own whitelisted number.
    * Test with Grandma's whitelisted number.
    * Test edge cases and sensitive information queries.

## 6. Future Considerations (Optional)

* **Voice Notes:** Explore allowing users to send WhatsApp voice notes, transcribing them to text before sending to Gemini.
* **Context Updates:** Plan a simple way to update the AI's knowledge base if new non-sensitive information needs to be added.
* **Error Monitoring/Alerting:** For a more robust system, basic error logging or alerting if the bot goes down.

## 7. Development Admin Interface

*   **Purpose:** To provide a developer-friendly interface for managing and inspecting project data during the development and testing phases. This interface is not intended for end-users (family members).
*   **Location:** `dev_tools/admin_interface/`
*   **Platform:** Locally hosted Web Application (e.g., using Flask or Streamlit).
*   **Key Features:**
    *   **System Prompt Management:**
        *   View the decrypted content of `agent_cli/system_prompt.md.enc`.
        *   Edit the system prompt content and save it back (re-encrypting automatically).
        *   Ability to encrypt an initial plain text system prompt file.
    *   **Notebook Context Management:**
        *   List all encrypted notebook files from `agent_cli/notebook_context/`.
        *   Select an encrypted file, view its decrypted content (using `agent_cli/encryption_service.py`).
        *   Edit the decrypted content and save it back (re-encrypting automatically).
        *   Potentially, allow uploading new plain text files (to `transcription_service/raw_transcriptions/` to follow the pipeline, or directly encrypt and save to `agent_cli/notebook_context/` for quick dev additions).
    *   **User Profile Management:**
        *   List all user profile files from `agent_cli/user
        _profiles/` (e.g., `*.json.enc`).
        *   View decrypted content of a selected user profile.
        *   Edit user profile details (e.g., name, preferred_name, pronouns) and save (re-encrypting).
        *   Add new user profiles (saved as encrypted JSON files).
    *   **Conversation Log Viewer:**
        *   Access and view conversation histories stored within encrypted user profiles in `agent_cli/user_profiles/`.
        *   Display conversations in a readable format.
*   **Security:**
    *   This tool will need access to the `ENCRYPTION_KEY` (likely from `agent_cli/.env` or its own configured environment) to perform decryption and encryption.
    *   The web application should be run locally and not exposed to the internet to maintain security.

## Instructions for Co-Pilot:

Always include docstrings for functions and methods.
Docstrings should contain:
- A brief, one-line description of what the function does.
- A section detailing each argument (`Args:`), its name, and description. Only include Args if they are not None.
- A section detailing the return value (`Returns:`), its type, and description. Only include Returns if they are not None.
Follow the standard docstring format for the language being used (e.g., Python's reST or Google style, JSDoc for JavaScript).

Always include type hints for function and method parameters when writing in Python.
Always include type hints for function and method return values when writing in Python.
Never include redundant comments denoting edits made such as "changed this" or "import x".

Always use UK english, not USA english.

Build code in a modular way from the start, with smaller already refactored files rather than monolithic files.

**Interacting with `TODO.md`:**
*   Be aware of the `TODO.md` file located in the project root.
*   When asked about project status, outstanding tasks, or next steps, consult `TODO.md` to provide informed responses.
*   If you complete a task that is listed in `TODO.md` as part of fulfilling a user request, please update the `TODO.md` file by marking the relevant item(s) as complete (e.g., change `[ ]` to `[x]`). Inform the user that you have updated the TODO list.
*   If a user request leads to new, clearly defined tasks that align with the project goals and are not yet on the list, you may suggest adding them to `TODO.md` or, if confident, add them directly and inform the user.
*   When adding items, try to follow the existing structure (Discrepancies & Fixes, New Features, etc.).
*   Always confirm with the user before making significant additions or structural changes to `TODO.md` beyond simple task completion.
*   ALWAYS update the TODO.md when completing tasks.

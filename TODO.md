# Agent-G Project TODO List

This list tracks discrepancies between the project specification and the current codebase, as well as new features to be implemented.

## I. Discrepancies & Fixes

### A. Directory Structure & File Locations
- [x] Rename `test_pictures/` to `pictures/` at the project root.
- [x] Create `transcription_service/raw_transcriptions/` directory.
- [x] Move contents of `test_transcribed_texts/` to `transcription_service/raw_transcriptions/` and then delete `test_transcribed_texts/`.
- [x] Create `agent_cli/notebook_context/` directory.
- [x] Move `user_profiles/` (currently at root) to `agent_cli/user_profiles/`.
- [x] Encrypt `agent_cli/system_prompt.md` and save it as `agent_cli/system_prompt.md.enc`. (The original plain text can be kept for reference or managed by the admin CLI later).

### B. Code Updates for New Structure
- [ ] **`agent_cli/config.py`:**
    - [x] Update `TRANSCRIPTION_DIR_NAME` to point to `\"notebook_context\"`.
    - [x] Update `TRANSCRIPTION_DIR` to use the new `TRANSCRIPTION_DIR_NAME`.
    - [x] Update `USER_PROFILE_DIR_NAME` to reflect it being inside `agent_cli` (if path construction relies on it, though `USER_PROFILE_DIR` might be correctly absolute). Verify `USER_PROFILE_DIR` points to `agent_cli/user_profiles/`.
    - [x] Update `SYSTEM_PROMPT_FILENAME` to `\"system_prompt.md.enc\"`.
    - [x] Ensure `SYSTEM_PROMPT_FILE_PATH` correctly points to `agent_cli/system_prompt.md.enc`.
- [ ] **`agent_cli/data_manager.py`:**
    - [x] Modify `load_transcriptions()` to read from `agent_cli/notebook_context/` (using `config.TRANSCRIPTION_DIR`) and expect only `.txt.enc` files, performing decryption using `encryption_service.decrypt_data`.
    - [x] Remove `save_transcription()`.
    - [x] Ensure `load_user_profile()` reads from `agent_cli/user_profiles/` (using `config.USER_PROFILE_DIR`) and handles `.json.enc` files by decrypting them.
    - [x] Ensure `save_user_profile()` writes to `agent_cli/user_profiles/` (using `config.USER_PROFILE_DIR`) and encrypts data if the filename ends with `.enc`.
    - [x] Implement logic to load and decrypt `agent_cli/system_prompt.md.enc` (new function `get_decrypted_system_prompt()`).
- [ ] **`agent_cli/llm_service.py`:**
    - [x] Update to use the new function from `data_manager.py` to get the decrypted system prompt.
- [ ] **`transcription_service/transcribe.py`:**
    - [x] Ensure its output directory is `transcription_service/raw_transcriptions/`.
    - [x] Ensure it outputs plain text files as per the spec.

## II. New Features Implementation

### A. `utilities/prepare_context.py` Script
- [x] Create `utilities/` directory.
- [x] Create `utilities/prepare_context.py`.
- [x] Implement logic to:
    - [x] Read plain text files from `transcription_service/raw_transcriptions/`.
    - [x] Import `encrypt_data` from `agent_cli.encryption_service`.
    - [x] Encrypt the content of each file.
    - [x] Save encrypted content to `agent_cli/notebook_context/[filename].txt.enc`.
    - [x] Handle potential errors (file not found, encryption errors).

### B. `dev_tools/admin_interface/` (Locally Hosted Web App)
- [x] Create `dev_tools/admin_interface/` directory.
- [x] Create main web application script (e.g., `dev_tools/admin_interface/app.py` using Flask or Streamlit).
- [x] Create `templates/` and `static/` directories if using Flask.
- [x] Add `requirements.txt` for web app dependencies (e.g., `Flask`, `Streamlit`).
- [x] Implement **System Prompt Management** (Web UI):
    - [x] Page/section to view decrypted `agent_cli/system_prompt.md.enc`.
    - [x] Page/section with a form to edit content and save back, re-encrypting.
- [x] Implement **Notebook Context Management** (Web UI):
    - [x] Page/section to list encrypted files in `agent_cli/notebook_context/`.
    - [x] Page/section to select a file and view its decrypted content.
    - [x] Page/section with a form to edit a selected file's content and save back, re-encrypting.
    - [x] Add a 'New File' button to /notebooks. Use the same editing interface, just have it spin up a new file , encrypt it, and add it to `agent_cli/notebook_context/`.
- [x] Implement **User Profile Management** (Web UI):
    - [x] Page/section to list encrypted user profiles in `agent_cli/user_profiles/`.
    - [x] Page/section to select a profile and view its decrypted JSON content (pretty-printed).
    - [x] Page/section with a form to edit user profile fields (e.g., name, preferred_name, pronouns) and save back, re-encrypting.
    - [x] Create New Profile Button
- [x] Ensure the Admin Web App uses `agent_cli.encryption_service` for all encryption/decryption.
- [x] Ensure robust error handling and a user-friendly web interface.
- [x] Ensure the web application is designed to be run locally and is not exposed to the internet.

### C. Core Agent Logic
- [ ] **Encryption of initial `system_prompt.md`**:
    - [ ] Manually create the initial plain text `system_prompt.md`.
    - [ ] Use the (to-be-created) Admin Web App to encrypt it into `agent_cli/system_prompt.md.enc`.
- [ ] **Loading decrypted system prompt**:
    - [ ] Ensure `agent_cli/llm_service.py` (or `agent_cli/data_manager.py`) correctly loads and decrypts `agent_cli/system_prompt.md.enc` for use.

### D. Future Considerations (Longer Term - from Spec)
- [ ] **WhatsApp Integration (Section 2.5, 5 of Spec):**
    - [ ] Twilio API setup.
    - [ ] Flask/FastAPI webhook in `agent_cli`.
    - [ ] Logic for receiving messages and sending replies via Twilio.
- [ ] **Hosting Setup (Section 5 of Spec):**
    - [ ] Prepare `agent_cli` for deployment (e.g., on PythonAnywhere).
- [ ] **Testing Framework (Section 3, 5 of Spec):**
    - [ ] Create `tests/` directory.
    - [ ] Add unit/integration tests for different modules.

This TODO list should provide a good roadmap for aligning the codebase with the specification and implementing the new features.

### C. Core Agent Logic
- [ ] **Encryption of initial `system_prompt.md`**:
    - [ ] Manually create the initial plain text `system_prompt.md`.
    - [ ] Use the (to-be-created) Admin Web App to encrypt it into `agent_cli/system_prompt.md.enc`.
- [ ] **Loading decrypted system prompt**:
    - [ ] Ensure `agent_cli/llm_service.py` (or `agent_cli/data_manager.py`) correctly loads and decrypts `agent_cli/system_prompt.md.enc` for use.

### D. Future Considerations (Longer Term - from Spec)
- [ ] **WhatsApp Integration (Section 2.5, 5 of Spec):**
    - [ ] Twilio API setup.
    - [ ] Flask/FastAPI webhook in `agent_cli`.
    - [ ] Logic for receiving messages and sending replies via Twilio.
- [ ] **Hosting Setup (Section 5 of Spec):**
    - [ ] Prepare `agent_cli` for deployment (e.g., on PythonAnywhere).
- [ ] **Testing Framework (Section 3, 5 of Spec):**
    - [ ] Create `tests/` directory.
    - [ ] Add unit/integration tests for different modules.

This TODO list should provide a good roadmap for aligning the codebase with the specification and implementing the new features.

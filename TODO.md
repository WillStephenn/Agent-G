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

### B. `dev_tools/admin_interface/` (CLI)
- [ ] Create `dev_tools/admin_interface/` directory.
- [ ] Create main CLI script (e.g., `dev_tools/admin_interface/admin_cli.py`).
- [ ] Add `requirements.txt` if specific dependencies are needed (e.g., `click`, `questionary`).
- [ ] Implement **System Prompt Management**:
    - [ ] Option to view decrypted `agent_cli/system_prompt.md.enc`.
    - [ ] Option to edit content (e.g., in a temporary file or via input) and save back, re-encrypting.
    - [ ] Option to encrypt an initial plain text system prompt file to `agent_cli/system_prompt.md.enc`.
- [ ] Implement **Notebook Context Management**:
    - [ ] Option to list encrypted files in `agent_cli/notebook_context/`.
    - [ ] Option to select a file and view its decrypted content.
    - [ ] Option to edit a selected file's content and save back, re-encrypting.
    - [ ] (Optional) Option to encrypt a new plain text file and add it to `agent_cli/notebook_context/`.
- [ ] Implement **User Profile Management**:
    - [ ] Option to list encrypted user profiles in `agent_cli/user_profiles/`.
    - [ ] Option to select a profile and view its decrypted JSON content (pretty-printed).
    - [ ] Option to edit user profile fields (e.g., name, preferred_name, pronouns) and save back, re-encrypting.
    - [ ] Option to add a new user profile (prompt for details, save as encrypted JSON).
- [ ] Implement **Conversation Log Viewer**:
    - [ ] Option to select a user profile.
    - [ ] View the conversation history from the selected profile in a readable format.
- [ ] Ensure the Admin CLI uses `agent_cli.encryption_service` for all encryption/decryption.
- [ ] Ensure robust error handling and user-friendly prompts.

### C. Core Agent Logic
- [ ] **Encryption of initial `system_prompt.md`**:
    - [ ] Manually create the initial plain text `system_prompt.md`.
    - [ ] Use the (to-be-created) Admin CLI to encrypt it into `agent_cli/system_prompt.md.enc`.
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

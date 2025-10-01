**Project Agent-G: A Digital Accessibility Bridge to Unorganised Handwritten Data**

Project Agent-G is conceived as a personal AI companion, inspired by the needs of my family, with an initial focus on supporting my Grandma (hence Agent G). Its purpose is to support in navigating large, handwritten notebooks containing Information left behind by my Grandpa. Agent-G is voiced as empathetic and understanding, meeting my Grandma where she is already comfortable; in a conversational manner.

Privacy and security are key considerations for this project. The system is built with Python, using Google's Gemini 2.5 Flash model via the Gemini API for its AI capabilities. Gemini 2.5 Flash was chosen for being fast, cost-effective, and falling well within the free tier limits for this use case.

## Data Pipeline and Workflow

The process of making the notebook content accessible involves several steps. First, handwritten pages are photographed. Before this, any sensitive information like passwords or financial details is covered with a "REDACTED" marker. An LLM (Gemini in this case) is then tasked with transcribing these images into digital text. This transcription process also identifies and preserves original spellings from the notebooks and marks the "REDACTED" sections. After a review, this digital text is encrypted and becomes the information base for Agent-G.

The core of Agent-G's functionality lies in its data pipeline and context management. The pipeline is as follows:
1.  **Image of Handwriting:** Physical notebook pages are photographed.
2.  **Intelligent Transcription Process:** The images are processed by a Gemini model that intelligently transcribes the handwriting, corrects typos while preserving the original text, and marks redacted information.
3.  **Encryption:** The transcribed text is then encrypted for security.
4.  **Context Loading:** The encrypted notebook transcriptions are loaded into the Gemini context window, along with the agent's personality and instructions, providing the AI with the necessary knowledge to answer user queries.

This data pipeline ensures that the information from the notebooks is accurately digitised, secured, and then effectively used by the AI to provide helpful and empathetic responses.

### Pipeline Visualisation: From Handwriting to Conversation

**Step 1: Handwritten Note**

![Handwritten Note Example](repo%20documentation%20content/[GreenNotebook]_Page[2].jpg)

*Original handwritten note from the Green Notebook test case, containing instructions about watering roses and the location of feed and a key.*

**Step 2: Transcribed and Corrected Text**

![Transcribed Notebook Example](repo%20documentation%20content/Admin%20Interface%20-%20Green%20Notebook%20Transcribed.png)

*The handwritten text is transcribed by Gemini, with original spellings preserved in `<original_text>` tags. Note how "teed" is corrected to "feed" while maintaining the original for reference.*

**Step 3: Context Loading and Conversational Query**

![Terminal Chat Example](repo%20documentation%20content/Terminal%20Chat%20Example.png)

*The transcribed content is loaded into the LLM's context window. When Isobel asks about the garage key location and watering schedule, Agent-G successfully retrieves the information from Richard's notes, demonstrating the complete pipeline from handwritten text to conversational AI response.*

## Admin Interface

It's designed to be secure and can be expanded to include more users in the future. A local admin interface, featuring a retro Macintosh System 1-inspired design, is available for developers to manage encrypted data and system settings. The interface runs locally on 127.0.0.1 and provides a clean, minimalist environment with monospaced fonts.

![Admin Interface Main Page](repo%20documentation%20content/Admin%20Interface%20Main%20Page.png)

*The main administration panel presents a simple menu with options to view and edit the system prompt, manage notebook context, and manage user profiles.*

### System Prompt Management

The system prompt defines Agent-G's core personality, behavior, and constraints. The AI is configured to be kind, patient, and empathetic, providing both general assistance and access to Richard Stephen's notebook transcriptions when relevant. The prompt includes critical instructions for handling sensitive information, particularly `<redacted_marker/>` tags, directing users to physical notebook locations rather than revealing redacted content. The interface enforces plain-text responses without markdown formatting to maintain a conversational, text-message-like style.

![System Prompt Editor](repo%20documentation%20content/Admin%20Interface%20-%20System%20Prompt%20Editor.png)

*The system prompt editor displays the complete instructions that govern Agent-G's responses, including personality traits, response style guidelines, and protocols for handling redacted information.*

### User Profile Management

User profiles store personal context, conversation history, and preferences to personalise Agent-G's interactions. Each profile is stored as an encrypted JSON file containing the user's name, pronouns, contextual information, and complete chat history. For example, Isobel Stephen's profile identifies her as Richard Stephen's widow and the primary system user, notes her need for patient explanations, includes information about her dog Max, and preserves her ongoing conversations with the AI.

![User Profile Page](repo%20documentation%20content/Admin%20Interface%20-%20User%20Profile%20Page.png)

*The user profiles section lists all encrypted profile files, with options to create new profiles or view existing ones.*

![User Profile with Context and Chat History](repo%20documentation%20content/Admin%20Interface%20-%20Isobel%20Profile.%20Context%20and%20Chat%20History.png)

*Viewing a decrypted profile reveals the complete JSON structure, including personal context, conversation history, and any redacted sensitive information (such as addresses).*

### Notebook Content Management

The interface provides tools to navigate, view, and edit encrypted notebook transcriptions. All notebook pages are stored as encrypted `.txt.enc` files and can be decrypted for viewing and editing within the admin interface. The transcription system preserves original text while noting corrections—for example, displaying both the original mistranscription "teed" and the correct word "feed" using `<original_text>` tags.

![Notebook Content Navigation](repo%20documentation%20content/Admin%20Interface%20-%20Notebook%20Content%20Navigation%20Page.png)

*The notebook management page lists all encrypted notebook files by identifier and page number, with options to create new entries.*

![Transcribed Notebook Example](repo%20documentation%20content/Admin%20Interface%20-%20Green%20Notebook%20Transcribed.png)

*Viewing a decrypted notebook page shows the transcribed content with preserved original spellings. This example, from a test case created on iPad, demonstrates instructions about watering roses, with the original mistranscription "teed" annotated before the corrected word "feed".*

## Terminal Chat Interface

Agent-G can be accessed through a command-line interface, providing a conversational experience for querying notebook content. Users can select their profile at startup, and the system loads their encrypted profile along with all available notebook transcriptions. The AI responds in a friendly, concise manner, drawing from Richard's notes to answer questions about practical information like key locations and plant care schedules.

![Terminal Chat Example](repo%20documentation%20content/Terminal%20Chat%20Example.png)

*A terminal session showing Isobel selecting her profile and asking about the garage key location and watering schedule. Agent-G successfully retrieves the information from Richard's notes, demonstrating the system's ability to bridge handwritten notebook content to conversational AI responses.*

## Getting Started

### Prerequisites

- Python 3.7 or higher
- A Google Gemini API key (obtain from [Google AI Studio](https://aistudio.google.com/))
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/WillStephenn/Agent-G.git
   cd Agent-G
   ```

2. **Set up the CLI environment:**
   ```bash
   cd agent_cli
   pip install -r requirements.txt
   ```

3. **Configure your environment variables:**
   
   Create a `.env` file in the `agent_cli` directory:
   ```bash
   touch .env
   ```
   
   Add your Gemini API key to the `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ENCRYPTION_KEY=your_base64_encoded_encryption_key_here
   ```
   
   **Note:** You'll need to generate your own encryption key. You can generate a secure key using Python:
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```

4. **Set up the Admin Interface (optional):**
   ```bash
   cd ../dev_tools/admin_interface
   pip install -r requirements.txt
   ```
   
   Create a `.env` file in the `dev_tools/admin_interface` directory with the same encryption key:
   ```
   ENCRYPTION_KEY=your_base64_encoded_encryption_key_here
   ```

### Running Agent-G

**CLI Mode:**
```bash
cd agent_cli
python cli.py
```

**Admin Interface:**
```bash
cd dev_tools/admin_interface
python app.py
```
Then navigate to `http://127.0.0.1:5000` in your web browser.

### Initial Setup

1. **Create a system prompt:** Use the admin interface to configure Agent-G's personality and behaviour
2. **Add notebook transcriptions:** Upload encrypted notebook content via the admin interface
3. **Create user profiles:** Set up profiles for each user who will interact with Agent-G
4. **Start chatting:** Launch the CLI and select your profile to begin conversing with Agent-G

**Note:** The example images shown in this README are not included in the repository for privacy reasons, but demonstrate the interface you'll see once you set up your own instance.

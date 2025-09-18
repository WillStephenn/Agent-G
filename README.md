**Project Agent-G: A Digital Accessibility Bridge to Unorganised Handwritten Data**

Project Agent-G is conceived as a personal AI companion, inspired by the needs of my family, with an initial focus on supporting my Grandma (hence Agent G). Its purpose is to support in navigating large, handwritten notebooks containing Information left behind by my Grandpa. Agent-G is voiced as empathetic and understanding, meeting my Grandma where she is already comfortable; in a conversational manner.

Privacy and security are key considerations for this project.

The process of making the notebook content accessible involves several steps. First, handwritten pages are photographed. Before this, any sensitive information like passwords or financial details is covered with a "REDACTED" marker. An LLM (Gemini in this case) is then tasked with transcribing these images into digital text. This transcription process also identifies and preserves original spellings from the notebooks and marks the "REDACTED" sections. After a review, this digital text is encrypted and becomes the information base for Agent-G.

The system is built with Python, using Google's Gemini API for its AI capabilities. It's designed to be secure and can be expanded to include more users in the future. A local admin interface is also available for developers to manage encrypted data and system settings. The project's aim is to offer a secure and useful tool for easily accessing the information within the notebooks.

The core of Agent-G's functionality lies in its data pipeline and context management. The pipeline is as follows:
1.  **Image of Handwriting:** Physical notebook pages are photographed.
2.  **Intelligent Transcription Process:** The images are processed by a Gemini model that intelligently transcribes the handwriting, corrects typos while preserving the original text, and marks redacted information.
3.  **Encryption:** The transcribed text is then encrypted for security.
4.  **Context Loading:** The encrypted notebook transcriptions are loaded into the Gemini context window, along with the agent's personality and instructions, providing the AI with the necessary knowledge to answer user queries.

This data pipeline ensures that the information from the notebooks is accurately digitised, secured, and then effectively used by the AI to provide helpful and empathetic responses.

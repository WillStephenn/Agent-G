**Project Agent-G: A Digital Accsibility Bridge to Unorganised Handwritten Data**

Project Agent-G is conceived as a personal AI companion, dedicated to helping the my family, with an initial focus on supporting my Grandma. Its purpose is to support in navigating notebooks containing Information left behind by my Grandpa. Agent-G is voiced as empathetic and understanding, meeting my Grandma where she is already comfortable; in a conversational manner on whatsapp.

Privacy and security are key considerations for this project.

The process of making the notebook content accessible involves several steps. First, handwritten pages are photographed. Before this, any sensitive information like passwords or financial details is covered with a "REDACTED" marker. An AI model (Gemini) then transcribes these images into digital text. This transcription process also identifies and preserves original spellings from the notebooks and marks the "REDACTED" sections. After a review, this digital text is encrypted and becomes the information base for Agent-G.

Family members on an approved list will interact with Agent-G via WhatsApp. The AI is designed to provide clear and simple responses. For questions about general notebook content, Agent-G will give direct answers. If a query relates to information marked "REDACTED", the AI will not provide the sensitive data. Instead, it will use the notebook and page number (derived from the source file's name) to tell the user where to find that information in the physical notebooks, keeping private details offline.

The system is built with Python, using Google's Gemini API for AI capabilities and the Twilio API for WhatsApp integration. It's designed to be secure and can be expanded to include more users in the future. A local admin interface will also be available for developers to manage encrypted data and system settings. The project's aim is to offer a secure and useful tool for easily accessing the information within the notebooks.

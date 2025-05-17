import os
import google.generativeai as genai
from PIL import Image
import pillow_heif
import dotenv
import re

pillow_heif.register_heif_opener()

# Load environment variables from .env file
dotenv.load_dotenv()

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in environment variables. Please set it in the .env file.")
    exit()
genai.configure(api_key=GEMINI_API_KEY)

# Define the Gemini model to be used
transcription_model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICTURES_DIR = os.path.join(BASE_DIR, "test_pictures")
TRANSCRIBED_TEXTS_DIR = os.path.join(BASE_DIR, "test_transcribed_texts")

# Ensure output directory exists
os.makedirs(TRANSCRIBED_TEXTS_DIR, exist_ok=True)

TRANSCRIPTION_PROMPT = """Your task is to transcribe the handwritten text from the provided image.

Follow these specific instructions carefully:

1.  **Accuracy:** Transcribe the text as accurately as possible.
2.  **Typo Correction & Original Text Preservation:** If you encounter obvious spelling errors or typos, please correct them in the main transcription. For each correction made, preserve the original as-transcribed word/phrase immediately after the corrected text, encapsulated within an XML-style tag: `<original_text>original uncorrected text</original_text>`.
    *   Example: "He went to the store `<original_text>stor</original_text>` to buy bread `<original_text> bred </original_text>`."
3.  **Redacted Information Handling:** If you encounter the word 'REDACTED' (transcribed from a physical cover slip in the image), transcribe it, but also encapsulate this specific word 'REDACTED' within an XML-style tag: `<redacted_marker/>`.
    *   Example: "...Password: <redacted_marker/>..."
4.  **Output Format:** Provide only the transcribed text with the specified XML tags. Do not include any other commentary or preamble.
"""

def sanitize_filename_component(name_part):
    """Removes problematic characters for filenames."""
    return re.sub(r'[\/*?:"<>|]', "", name_part)

def transcribe_image(image_path):
    """
    Transcribes a single image using Gemini API and saves the result.
    """
    try:
        print(f"Processing image: {image_path}...")
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return

    try:
        # Extract NotebookIdentifier and PageNumber from the image filename
        # Expected format: BlueNotebook_Page023.jpg
        filename = os.path.basename(image_path)
        name_part, _ = os.path.splitext(filename) # Remove extension
        
        parts = name_part.split('_Page')
        if len(parts) != 2:
            print(f"Warning: Could not parse NotebookIdentifier and PageNumber from filename: {filename}. Skipping.")
            return

        # Clean notebook_identifier and page_number_str by removing brackets
        cleaned_notebook_identifier = parts[0].replace('[', '').replace(']', '')
        cleaned_page_number_str = parts[1].replace('[', '').replace(']', '')

        notebook_identifier = sanitize_filename_component(cleaned_notebook_identifier)
        # Ensure page_number_str is the cleaned version for isdigit() check and int conversion
        page_number_str = sanitize_filename_component(cleaned_page_number_str) 

        if not notebook_identifier or not page_number_str.isdigit():
            print(f"Warning: Invalid NotebookIdentifier or PageNumber from filename: {filename} (Parsed: '{notebook_identifier}', '{page_number_str}'). Skipping.")
            return
            
        page_number = int(page_number_str) # Keep as int for now, format later

        # Generate response from Gemini
        print(f"  Sending to Gemini for transcription...")
        response = transcription_model.generate_content([TRANSCRIPTION_PROMPT, img], stream=False)
        response.resolve() # Ensure the response is fully available

        if not response.candidates or not response.candidates[0].content.parts:
            print(f"  Error: No content returned from Gemini for {filename}.")
            return
            
        transcribed_text = response.text.strip()

        # Output filename convention: [NotebookIdentifier]___[PageNumber].txt
        # Zero-padding page numbers for consistent sorting (e.g., Page023)
        output_filename = f"{notebook_identifier}___Page{page_number:03d}.txt"
        output_filepath = os.path.join(TRANSCRIBED_TEXTS_DIR, output_filename)

        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(transcribed_text)
        print(f"  Successfully transcribed and saved to: {output_filepath}")

    except Exception as e:
        print(f"  An error occurred during transcription or saving for {image_path}: {e}")

def main():
    print("Starting transcription process...")
    print(f"Looking for images in: {PICTURES_DIR}")
    print(f"Saving transcriptions to: {TRANSCRIBED_TEXTS_DIR}")

    if not os.path.exists(PICTURES_DIR):
        print(f"Error: Pictures directory not found at {PICTURES_DIR}. Please create it and add images.")
        return

    processed_files = 0
    for filename in os.listdir(PICTURES_DIR):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".heic", ".webp")):
            image_path = os.path.join(PICTURES_DIR, filename)
            transcribe_image(image_path)
            processed_files +=1
    
    if processed_files == 0:
        print(f"No image files found in {PICTURES_DIR}. Please add images (e.g., .jpg, .png).")
    else:
        print(f"Transcription process completed. Processed {processed_files} image(s).")

if __name__ == "__main__":
    main()

import os
import google.generativeai as genai
from PIL import Image
import pillow_heif
import dotenv
import re

pillow_heif.register_heif_opener()

dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env.")
    exit()
genai.configure(api_key=GEMINI_API_KEY)

TRANSCRIPTION_TEMPERATURE = 0.7
transcription_model = genai.GenerativeModel(
    "gemini-2.5-flash-preview-04-17",
    generation_config=genai.types.GenerationConfig(temperature=TRANSCRIPTION_TEMPERATURE)
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICTURES_DIR = os.path.join(BASE_DIR, "pictures")
TRANSCRIBED_TEXTS_DIR = os.path.join(BASE_DIR, "transcription_service", "raw_transcriptions")

os.makedirs(TRANSCRIBED_TEXTS_DIR, exist_ok=True)

TRANSCRIPTION_PROMPT = """Your task is to transcribe the handwritten text from the provided image.

Follow these specific instructions carefully:

1.  Accuracy: Transcribe the text as accurately as possible.
2.  Typo Correction & Original Text Preservation:** If you encounter obvious spelling errors or typos, please correct them in the main transcription. For each correction made, preserve the original as-transcribed word/phrase immediately after the corrected text, encapsulated within an XML-style tag: `<original_text>original uncorrected text</original_text>`.
    *   Example: "He went to the store `<original_text>stor</original_text>` to buy bread `<original_text> bred </original_text>`."
3.  Redacted Information Handling:** If you encounter the word 'REDACTED' (transcribed from a physical cover slip in the image), transcribe it, but also encapsulate this specific word 'REDACTED' within an XML-style tag: `<redacted_marker/>`.
    *   Example: "...Password: <redacted_marker/>..."
4.  Merged Word Handling:** If you identify words that have been incorrectly merged (e.g., "bookkeeper" instead of "book keeper"), please split them into their correct constituent words in the main transcription. For each such correction, preserve the original merged word immediately after the corrected (split) text, encapsulated within an XML-style tag: `<original_text>original merged word</original_text>`.
    *   Example: "Contact the book keeper `<original_text>bookkeeper</original_text>` for details."
5.  Output Format: Provide only the transcribed text with the specified XML tags. Do not include any other commentary or preamble.
"""

def sanitise_filename_component(name_part: str) -> str:
    """Removes problematic characters for filenames, including brackets.

    Args:
        name_part (str): The string to sanitise.

    Returns:
        str: The sanitised string.
    """
    return str(re.sub(r'[\\/*?:"<>|\[\]]', "", name_part))

def transcribe_image(image_path: str, transcribed_texts_dir: str = TRANSCRIBED_TEXTS_DIR) -> None:
    """Transcribes a single image using Gemini API and saves the result.

    Args:
        image_path (str): The absolute path to the image file.
        transcribed_texts_dir (str): Directory to save the transcription.
            Defaults to TRANSCRIBED_TEXTS_DIR.
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
        filename = os.path.basename(image_path)
        name_part, _ = os.path.splitext(filename)
        
        parts = name_part.split('_Page')
        if len(parts) != 2:
            print(f"Warning: Could not parse NotebookIdentifier and PageNumber from filename: {filename}. Skipping.")
            return

        notebook_identifier = sanitise_filename_component(parts[0])
        page_number_str = sanitise_filename_component(parts[1])

        if not notebook_identifier or not page_number_str.isdigit():
            print(f"Warning: Invalid NotebookIdentifier or PageNumber from filename: {filename} (Parsed: '{notebook_identifier}', '{page_number_str}'). Skipping.")
            return
            
        page_number = int(page_number_str)

        print(f"  Sending to Gemini for transcription...")
        response = transcription_model.generate_content([TRANSCRIPTION_PROMPT, img], stream=False)
        response.resolve()

        if not response.candidates or not response.candidates[0].content.parts:
            print(f"  Error: No content returned from Gemini for {filename}.")
            return
            
        transcribed_text = response.text.strip()

        output_filename = f"{notebook_identifier}___Page{page_number:03d}.txt"
        output_filepath = os.path.join(transcribed_texts_dir, output_filename)

        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(transcribed_text)
        print(f"  Successfully transcribed and saved to: {output_filepath}")

    except Exception as e:
        print(f"  An error occurred during transcription or saving for {image_path}: {e}")

def process_images(pictures_dir: str = PICTURES_DIR, transcribed_texts_dir: str = TRANSCRIBED_TEXTS_DIR) -> None:
    """Processes all images in the specified directory, transcribes them, and saves the results.

    Args:
        pictures_dir (str): Directory containing images to transcribe.
            Defaults to PICTURES_DIR.
        transcribed_texts_dir (str): Directory to save transcriptions.
            Defaults to TRANSCRIBED_TEXTS_DIR.
    """
    print("Starting transcription process...")
    print(f"Looking for images in: {pictures_dir}")
    print(f"Saving transcriptions to: {transcribed_texts_dir}")

    if not os.path.exists(pictures_dir):
        print(f"Error: Pictures directory not found at {pictures_dir}. Please create it and add images.")
        return

    processed_files = 0
    for filename in os.listdir(pictures_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".heic", ".webp")):
            image_path = os.path.join(pictures_dir, filename)
            transcribe_image(image_path, transcribed_texts_dir)
            processed_files += 1

    if processed_files == 0:
        print(f"No image files found in {pictures_dir}. Please add images (e.g., .jpg, .png).")
    else:
        print(f"Transcription process completed. Processed {processed_files} image(s).")

def main() -> None:
    """Main function to orchestrate the transcription process.

    Reads images from the `PICTURES_DIR`, transcribes them using `transcribe_image`,
    and saves the transcriptions to `TRANSCRIBED_TEXTS_DIR`.
    """
    process_images()

if __name__ == "__main__":
    main()


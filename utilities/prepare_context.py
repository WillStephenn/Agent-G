import os
import sys
from dotenv import load_dotenv

# Determine project root and paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
AGENT_CLI_DIR = os.path.join(PROJECT_ROOT, "agent_cli")
DOTENV_PATH = os.path.join(AGENT_CLI_DIR, ".env")

# Load environment variables from agent_cli/.env
if load_dotenv(dotenv_path=DOTENV_PATH):
    print(f"Loaded environment variables from {DOTENV_PATH}")
else:
    print(f"Warning: .env file not found at {DOTENV_PATH} or it is empty. The ENCRYPTION_KEY might not be available for encryption_service.")

# Add project root to sys.path
sys.path.append(PROJECT_ROOT)

# Attempt to import encryption_service
try:
    from agent_cli.encryption_service import encrypt_data
except ImportError as e:
    print(f"Error: Could not import encrypt_data from agent_cli.encryption_service: {e}")
    print("Ensure that 'agent_cli' is a package in the project root and encryption_service.py exists within it.")
    print("Also, ensure that the project root directory is in your PYTHONPATH or accessible via sys.path.")
    sys.exit(1)
except ValueError as e:
    print(f"Error during import of encryption_service: {e}")
    print(f"Please ensure that ENCRYPTION_KEY is correctly set in {DOTENV_PATH} and the file is accessible.")
    sys.exit(1)


# Define paths relative to the project root
RAW_TRANSCRIPTIONS_DIR = os.path.join(PROJECT_ROOT, "transcription_service", "raw_transcriptions")
NOTEBOOK_CONTEXT_DIR = os.path.join(PROJECT_ROOT, "agent_cli", "notebook_context")


def prepare_context() -> None:
    """
    Reads plain text files from raw_transcriptions, encrypts, and saves them to notebook_context.

    This function processes .txt files from the RAW_TRANSCRIPTIONS_DIR, encrypts their
    content using the `encrypt_data` function (which is expected to use an
    ENCRYPTION_KEY from the environment), and saves the encrypted content into
    the NOTEBOOK_CONTEXT_DIR with a .enc extension.

    Args:
        None

    Returns:
        None
    """
    if not os.path.exists(RAW_TRANSCRIPTIONS_DIR):
        print(f"Error: Source directory for raw transcriptions not found: {RAW_TRANSCRIPTIONS_DIR}")
        return

    if not os.path.isdir(RAW_TRANSCRIPTIONS_DIR):
        print(f"Error: Source path for raw transcriptions is not a directory: {RAW_TRANSCRIPTIONS_DIR}")
        return

    if not os.path.exists(NOTEBOOK_CONTEXT_DIR):
        try:
            os.makedirs(NOTEBOOK_CONTEXT_DIR)
            print(f"Created destination directory: {NOTEBOOK_CONTEXT_DIR}")
        except OSError as e:
            print(f"Error: Could not create destination directory {NOTEBOOK_CONTEXT_DIR}: {e}")
            return
    elif not os.path.isdir(NOTEBOOK_CONTEXT_DIR):
        print(f"Error: Destination path for notebook context is not a directory: {NOTEBOOK_CONTEXT_DIR}")
        return

    print(f"Starting context preparation...")
    print(f"Reading plain text files from: {RAW_TRANSCRIPTIONS_DIR}")
    print(f"Encrypting and writing to: {NOTEBOOK_CONTEXT_DIR}")

    processed_files_count = 0
    failed_files_count = 0

    for filename in os.listdir(RAW_TRANSCRIPTIONS_DIR):
        if filename.endswith(".txt"):
            source_filepath = os.path.join(RAW_TRANSCRIPTIONS_DIR, filename)
            output_filename = f"{filename}.enc"
            output_filepath = os.path.join(NOTEBOOK_CONTEXT_DIR, output_filename)

            try:
                with open(source_filepath, "r", encoding="utf-8") as f_in:
                    content = f_in.read()
                
                content_bytes = content.encode("utf-8")
                
                encrypted_content = encrypt_data(content_bytes)

                with open(output_filepath, "wb") as f_out:
                    f_out.write(encrypted_content)
                
                print(f"Successfully processed and encrypted: {filename} -> {output_filename}")
                processed_files_count += 1
            except FileNotFoundError:
                print(f"Error: Source file not found: {source_filepath}")
                failed_files_count += 1
            except IOError as e:
                print(f"Error reading from {source_filepath} or writing to {output_filepath}: {e}")
                failed_files_count += 1
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                failed_files_count += 1
        else:
            pass
            
    print(f"\nContext preparation complete.")
    print(f"Successfully processed files: {processed_files_count}")
    print(f"Failed files: {failed_files_count}")

if __name__ == "__main__":
    print("Running prepare_context.py script...")
    prepare_context()
    print("Script finished.")


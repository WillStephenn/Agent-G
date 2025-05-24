"""
Main Flask application for the Agent-G Admin Interface.

This application provides a web-based interface for managing and inspecting
project data, including system prompts, notebook contexts, and user profiles.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sys
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Adjust path to import from agent_cli
# This assumes dev_tools and agent_cli are in the same parent directory (Agent G)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir)) # Moves up two levels to Agent G/
sys.path.append(project_root)

# Load .env file from agent_cli directory
dotenv_path = os.path.join(project_root, 'agent_cli', '.env')
load_dotenv(dotenv_path)

# encryption_service now handles its own key loading.
# If it fails to load its key, it will raise an error on import or use.
from agent_cli.encryption_service import decrypt_data, encrypt_data
from agent_cli.config import SYSTEM_PROMPT_FILE_PATH # For system prompt path

# Configuration for notebook context
NOTEBOOK_CONTEXT_DIR = os.path.join(os.path.dirname(__file__), '''../../agent_cli/notebook_context/''')
if not os.path.exists(NOTEBOOK_CONTEXT_DIR):
    os.makedirs(NOTEBOOK_CONTEXT_DIR)

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index() -> str:
    """Renders the main index page of the admin interface.

    Returns:
        str: Rendered HTML page with navigation links.
    """
    return render_template('index.html')

@app.route('/view_system_prompt')
def view_system_prompt() -> str:
    """Reads, decrypts, and displays the system prompt.

    Returns:
        str: Rendered HTML page displaying the system prompt or an error message.
    """
    try:
        with open(SYSTEM_PROMPT_FILE_PATH, 'rb') as f:
            encrypted_prompt = f.read()
        
        decrypted_prompt_bytes = decrypt_data(encrypted_prompt)
        decrypted_prompt = decrypted_prompt_bytes.decode('utf-8')
        return render_template('view_system_prompt.html', prompt_content=decrypted_prompt)
    except FileNotFoundError:
        return render_template('view_system_prompt.html', prompt_content="ERROR: System prompt file not found.")
    except Exception as e:
        # Log the exception e for debugging if necessary
        return render_template('view_system_prompt.html', prompt_content=f"ERROR: Could not decrypt or read system prompt: {str(e)}")

@app.route('/edit_system_prompt', methods=['GET', 'POST'])
def edit_system_prompt() -> str:
    """Handles editing and saving the system prompt.

    GET: Displays a form pre-filled with the current decrypted system prompt.
    POST: Saves the submitted prompt content after encrypting it.

    Returns:
        str: Rendered HTML page. On POST success, redirects to view_system_prompt.
             On error, re-renders the edit page with an error message.
    """
    if request.method == 'POST':
        new_prompt_content = request.form['prompt_content']
        try:
            encrypted_new_prompt = encrypt_data(new_prompt_content.encode('utf-8'))
            with open(SYSTEM_PROMPT_FILE_PATH, 'wb') as f:
                f.write(encrypted_new_prompt)
            # Add a success message if desired, e.g., using flash messages
            flash("System prompt updated successfully.", "success")
            return redirect(url_for('view_system_prompt'))
        except Exception as e:
            # Log error, pass error message to template
            flash(f"Error saving prompt: {str(e)}", "error")
            return render_template(
                'edit_system_prompt.html', 
                current_prompt_content=new_prompt_content, 
                error_message=f"Error saving prompt: {str(e)}"
            )

    # GET request logic
    try:
        with open(SYSTEM_PROMPT_FILE_PATH, 'rb') as f:
            encrypted_prompt = f.read()
        decrypted_prompt_bytes = decrypt_data(encrypted_prompt)
        decrypted_prompt = decrypted_prompt_bytes.decode('utf-8')
        return render_template('edit_system_prompt.html', current_prompt_content=decrypted_prompt)
    except FileNotFoundError:
        flash("ERROR: System prompt file not found. Cannot edit.", "error")
        return render_template('edit_system_prompt.html', current_prompt_content="", error_message="ERROR: System prompt file not found. Cannot edit.")
    except Exception as e:
        flash(f"ERROR: Could not decrypt or read system prompt: {str(e)}", "error")
        return render_template('edit_system_prompt.html', current_prompt_content="", error_message=f"ERROR: Could not decrypt or read system prompt: {str(e)}")

@app.route('/notebooks')
def list_notebooks() -> str:
    """Lists encrypted notebook files from the notebook_context directory.

    Returns:
        str: Rendered HTML page displaying the list of notebook files or an error message.
    """
    try:
        if not os.path.exists(NOTEBOOK_CONTEXT_DIR):
            flash(f"Notebook context directory not found: {NOTEBOOK_CONTEXT_DIR}", "error")
            return render_template('list_notebooks.html', files=[])

        files = [f for f in os.listdir(NOTEBOOK_CONTEXT_DIR) if os.path.isfile(os.path.join(NOTEBOOK_CONTEXT_DIR, f)) and f.endswith(".txt.enc")]
        return render_template('list_notebooks.html', files=files)
    except Exception as e:
        flash(f"Error listing notebook files: {str(e)}", "error")
        return render_template('list_notebooks.html', files=[])

@app.route('/notebooks/<filename>')
def view_notebook_route(filename: str) -> str:
    """Displays the decrypted content of a specific notebook file.

    Args:
        filename (str): The name of the notebook file to view. It should be
                        a secure filename.

    Returns:
        str: Rendered HTML page displaying the notebook content, or a redirect
             to the notebook list on error.
    """
    file_path = os.path.join(NOTEBOOK_CONTEXT_DIR, secure_filename(filename))
    try:
        with open(file_path, 'rb') as f:
            encrypted_content = f.read()
        
        # Directly use the decrypt_data function.
        # If encryption_service.py had an issue loading its key,
        # an error would likely have occurred during its import,
        # or this decrypt_data call will fail.
        decrypted_content_bytes = decrypt_data(encrypted_content)
        decrypted_content = decrypted_content_bytes.decode('utf-8')
        return render_template('view_notebook.html', filename=filename, content=decrypted_content, error=False)
    except FileNotFoundError:
        flash(f"Notebook file '{filename}' not found.", "error")
        return redirect(url_for('list_notebooks'))
    except Exception as e:
        # This can catch errors from decrypt_data (e.g., invalid key, corrupted data)
        # or file I/O issues.
        app.logger.error(f"Error viewing notebook {filename}: {e}", exc_info=True)
        flash(f"An error occurred while trying to view notebook '{filename}'. "
              "This could be due to corrupted content, an issue with the encryption key "
              "(ensure ENCRYPTION_KEY in agent_cli/.env is correct and accessible to the encryption service), "
              "or the file not being properly encrypted. Check server logs for details.", "error")
        # Optionally, render the error on the same page or redirect
        return render_template('view_notebook.html', filename=filename, content=f"Error: {str(e)}", error=True)

@app.route('/notebooks/<filename>/edit', methods=['GET', 'POST'])
def edit_notebook_route(filename: str) -> str:
    """Handles editing and saving a specific notebook file.

    GET: Displays a form pre-filled with the current decrypted notebook content.
    POST: Saves the submitted notebook content after encrypting it.

    Args:
        filename (str): The name of the notebook file to edit. It should be
                        a secure filename.

    Returns:
        str: Rendered HTML page. On POST success, redirects to view_notebook.
             On error, re-renders the edit page with an error message.
    """
    secure_file = secure_filename(filename)
    file_path = os.path.join(NOTEBOOK_CONTEXT_DIR, secure_file)
    
    if request.method == 'POST':
        new_content = request.form['notebook_content']
        try:
            encrypted_new_content = encrypt_data(new_content.encode('utf-8'))
            with open(file_path, 'wb') as f:
                f.write(encrypted_new_content)
            flash(f"Notebook '{filename}' updated successfully.", "success")
            return redirect(url_for('view_notebook_route', filename=filename))
        except Exception as e:
            flash(f"Error saving notebook: {str(e)}", "error")
            return render_template(
                'edit_notebook.html', 
                filename=filename,
                current_content=new_content, 
                error_message=f"Error saving notebook: {str(e)}"
            )

    # GET request logic
    try:
        with open(file_path, 'rb') as f:
            encrypted_content = f.read()
        decrypted_content_bytes = decrypt_data(encrypted_content)
        decrypted_content = decrypted_content_bytes.decode('utf-8')
        return render_template('edit_notebook.html', filename=filename, current_content=decrypted_content)
    except FileNotFoundError:
        flash(f"Notebook file '{filename}' not found. Cannot edit.", "error")
        return redirect(url_for('list_notebooks'))
    except Exception as e:
        flash(f"ERROR: Could not decrypt or read notebook '{filename}': {str(e)}", "error")
        return render_template('edit_notebook.html', filename=filename, current_content="", error_message=f"ERROR: Could not decrypt or read notebook '{filename}': {str(e)}")

@app.route('/notebooks/new', methods=['GET', 'POST'])
def new_notebook_route() -> str:
    """Handles creating a new notebook file.

    GET: Displays a form for entering the new notebook filename and content.
    POST: Creates the new notebook file, encrypts the content, and saves it.
    """
    if request.method == 'POST':
        filename = request.form.get('filename')
        content = request.form.get('notebook_content', '') # Default to empty string if not provided

        if not filename:
            flash("Filename is required.", "error")
            return render_template('edit_notebook.html', filename="", current_content=content, error_message="Filename is required.", is_new=True)

        # Basic validation for filename (e.g., no slashes, has .txt.enc)
        if '/' in filename or '\\\\' in filename:
            flash("Filename cannot contain slashes.", "error")
            return render_template('edit_notebook.html', filename=filename, current_content=content, error_message="Filename cannot contain slashes.", is_new=True)
        
        if not filename.endswith(".txt.enc"):
            filename += ".txt.enc"
            
        secure_file = secure_filename(filename)
        file_path = os.path.join(NOTEBOOK_CONTEXT_DIR, secure_file)

        if os.path.exists(file_path):
            flash(f"A notebook with the name '{secure_file}' already exists. Please choose a different name.", "error")
            return render_template('edit_notebook.html', filename=filename, current_content=content, error_message=f"File '{secure_file}' already exists.", is_new=True)

        try:
            encrypted_content = encrypt_data(content.encode('utf-8'))
            with open(file_path, 'wb') as f:
                f.write(encrypted_content)
            flash(f"Notebook '{secure_file}' created successfully.", "success")
            return redirect(url_for('view_notebook_route', filename=secure_file))
        except Exception as e:
            flash(f"Error creating notebook: {str(e)}", "error")
            # Pass is_new=True to ensure the template renders correctly for a new file scenario
            return render_template('edit_notebook.html', filename=filename, current_content=content, error_message=f"Error creating notebook: {str(e)}", is_new=True)

    # GET request: Show a form to create a new notebook
    # We can reuse the edit_notebook.html template if we adapt it slightly
    # or create a new one. For simplicity, let's try to adapt edit_notebook.html
    # by passing a new flag, e.g., `is_new=True`.
    return render_template('edit_notebook.html', filename="", current_content="", is_new=True)


if __name__ == '__main__':
    # Note: Debug mode should be False in a production environment or if exposed.
    # For local development, True is acceptable.
    app.run(debug=True)


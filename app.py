import os
from flask import Flask, request, send_from_directory, render_template, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os.path
import zipfile
import shutil

# Import the bundle_pages function from your original script
from bundle_pages import bundle_pages as run_splitter


UPLOAD_FOLDER = '/home/user/Documents/Work_Order_PDF_Splitter_V1_Finished/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

OUTPUT_FOLDER = '/home/user/Documents/Work_Order_PDF_Splitter_V1_Finished/output'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'some_secret_key'

def get_output_files():
    files = os.listdir(OUTPUT_FOLDER)
    files = [file for file in files if file.endswith('.pdf')]
    return files

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if request.files:
            file = request.files['file']
            if file.filename == "":
                return "No file selected for uploading"

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                input_pdf_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(input_pdf_path)

                output_directory = app.config['OUTPUT_FOLDER']
                run_splitter(input_pdf_path, output_directory)
                output_files = os.listdir(output_directory)

                if output_files:
                    zip_filename = create_zip(output_directory)
                    output_files.insert(0, zip_filename)
                    print(f"Serving file: {output_files[0]}")
                    return redirect(url_for('download_file', filename=output_files[0]))

                else:
                    return "Error processing file: No output files generated."
            else:
                return "Error processing file: Invalid file format."
                   
        else:
            return "Error processing file: No files found in request."
    else:  # request.method == 'GET'
        output_files = [f for f in os.listdir('output') if os.path.isfile(os.path.join('output', f))]
        output_files = get_output_files() 
        if output_files:
            zip_filename = create_zip(app.config['OUTPUT_FOLDER'])
        else:
            zip_filename = None
        return render_template('index.html', output_files=output_files, zip_filename=zip_filename, title="James' Super Handy Work Order PDF Splitter")



@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

@app.route('/delete', methods=['POST'])
def delete_files():
    directory = app.config['OUTPUT_FOLDER']
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
    print(f"All files in {directory} have been deleted.")
    return redirect('/')



@app.route('/output/<path:filename>')
def serve_output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

    title = "James' Super Handy Work Order PDF Splitter"

    return render_template('index.html')

def create_zip(output_directory):
    zip_filename = 'output_files.zip'
    zip_file_path = os.path.join(output_directory, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, _, files in os.walk(output_directory):
            for file in files:
                if file == zip_filename:
                    continue
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, output_directory))
    return zip_filename


if __name__ == '__main__':
    app.run(debug=True)
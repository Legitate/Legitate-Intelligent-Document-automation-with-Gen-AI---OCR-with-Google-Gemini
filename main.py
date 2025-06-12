from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from extractor import extract_data_from_pdf_gemini

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "Invoice Extraction Backend Running"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    result = extract_data_from_pdf_gemini(file_path)

    if result is None:
        return jsonify({'error': 'Failed to extract data'}), 500

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

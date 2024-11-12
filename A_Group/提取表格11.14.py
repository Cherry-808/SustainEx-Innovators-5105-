from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Set the upload folder and allowed extensions
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}  # Allow only PDF files
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload file API
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Check if the filename is empty
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Validate file extension
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed."}), 400

    # Save file to the upload folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    # Return a success response
    return jsonify({"message": "File uploaded successfully!", "file_path": file_path}), 200


@app.route('/')
def home():
    return "欢迎访问首页！"

@app.route('/results')
def results():
    return "这是结果页面"

@app.route('/favicon.ico')
def favicon():
    return '', 204  # 无内容响应
    
# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
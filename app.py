from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from rag_utils import (
    process_and_store_pdf,
    get_uploaded_files,
    get_answer,
    get_chunks_for_file,
    get_summary_for_file,
    get_metadata_for_file
)

app = Flask(__name__)
CORS(app)

# Directory to store uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------- File Upload Route ----------------------

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Uploads a PDF or text file, processes it, and returns its metadata and summary.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
    file.save(file_path)

    # Process the uploaded file for text extraction and chunking
    process_and_store_pdf(file_path)
    file_id = os.path.splitext(filename)[0]

    return jsonify({
        "message": f"{filename} uploaded successfully",
        "file_name": filename,
        "file_type": os.path.splitext(filename)[1].lower(),
        "summary": get_summary_for_file(file_id),
        "metadata": get_metadata_for_file(file_id)
    }), 200

# ---------------------- List Uploaded Files ----------------------

@app.route("/files", methods=["GET"])
def list_files():
    """
    Returns a list of all uploaded files.
    """
    return jsonify(get_uploaded_files())

# ---------------------- Retrieve File Chunks ----------------------

@app.route("/chunks/<file_id>", methods=["GET"])
def get_chunks(file_id):
    """
    Returns all extracted text chunks for a given file ID.
    """
    return jsonify({"chunks": get_chunks_for_file(file_id)})

# ---------------------- File Summary and Metadata ----------------------

@app.route("/summary/<file_id>", methods=["GET"])
def get_summary(file_id):
    """
    Returns the summary and metadata for a given file.
    """
    return jsonify({
        "summary": get_summary_for_file(file_id),
        "metadata": get_metadata_for_file(file_id)
    })

# ---------------------- Ask Question About File ----------------------

@app.route("/ask", methods=["POST"])
def ask():
    """
    Receives a question and file ID, returns an answer with source chunks.
    """
    data = request.get_json()
    file_id = data.get("file_id", "")
    question = data.get("question", "")
    chat_history = data.get("chat_history", [])

    if not file_id or not question:
        return jsonify({"error": "Missing file_id or question"}), 400

    answer, sources, updated_history = get_answer(file_id, question, chat_history)

    return jsonify({
        "answer": answer,
        "sources": sources,
        "chat_history": updated_history
    })

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from rag_utils import (
    process_and_store_pdf,
    get_uploaded_files,
    get_answer,
    get_chunks_for_file,
    get_summary_for_file,
)

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    saved_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(saved_path)
    process_and_store_pdf(saved_path)

    return jsonify({
        "message": f"{file.filename} uploaded successfully",
        "file_name": file.filename,
        "file_type": os.path.splitext(file.filename)[1].lower(),
        "summary": get_summary_for_file(os.path.splitext(file.filename)[0])
    }), 200

@app.route("/files", methods=["GET"])
def list_files():
    files = get_uploaded_files()
    # Return just a simple list of file IDs (strings)
    return jsonify(files)

@app.route("/chunks/<file_id>", methods=["GET"])
def get_chunks(file_id):
    chunks = get_chunks_for_file(file_id)
    return jsonify({"chunks": chunks})

@app.route("/summary/<file_id>", methods=["GET"])
def get_summary(file_id):
    summary = get_summary_for_file(file_id)
    # You can add metadata here if needed, e.g. return a dict with metadata and summary
    return jsonify({
        "metadata": f"Metadata for {file_id}",  # Replace with real metadata if available
        "summary": summary
    })

@app.route("/ask", methods=["POST"])
def ask():
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

import gradio as gr
import requests
import os

# Base URL of the backend API
API_URL = "http://127.0.0.1:5000"

# ------------------ Upload File ------------------

def upload_file(file):
    """
    Uploads a PDF or text file to the backend API.
    """
    if not file:
        return "No file selected."
    
    file_type = "pdf" if file.name.endswith(".pdf") else "text"
    file_name = os.path.basename(file.name)

    with open(file.name, "rb") as f:
        files = {"file": (file_name, f, f"application/{file_type}")}
        response = requests.post(f"{API_URL}/upload", files=files)

    if response.status_code == 200:
        return f"{file_name} uploaded successfully."
    else:
        return f"Upload failed: {response.text}"

# ------------------ List Uploaded Files ------------------

def get_uploaded_files():
    """
    Fetches list of uploaded file IDs from the backend.
    """
    try:
        response = requests.get(f"{API_URL}/files")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

# ------------------ Refresh Dropdown ------------------

def update_dropdown():
    """
    Refreshes the file dropdown with the latest file list.
    """
    files = get_uploaded_files()
    return gr.update(choices=files, value=None)

# ------------------ Metadata & Summary ------------------

def get_summary_and_metadata(file_id):
    """
    Retrieves summary and metadata for the selected file.
    
    """
    if not file_id:
        return "No file selected.", "No file selected."

    try:
        response = requests.get(f"{API_URL}/summary/{file_id}")
        if response.status_code == 200:
            data = response.json()
            metadata = data.get("metadata", {})
            summary = data.get("summary", "No summary available.")

            # Format metadata nicely
            meta_lines = [
                f"{key.replace('_', ' ').title()}: {val}" for key, val in metadata.items()
            ]
            metadata_str = "\n".join(meta_lines)

            # Trim long summaries
            summary_lines = summary.splitlines()
            trimmed_summary = "\n".join(summary_lines[:5])

            return metadata_str, trimmed_summary
    except Exception as e:
        return f"Error: {str(e)}", "Summary error."
    
    return "Error fetching metadata.", "Error fetching summary."

# ------------------ Chunks Preview ------------------

def get_chunks(file_id):
    """
    Fetches document chunks from the backend for preview.
    """
    if not file_id:
        return "No file selected."

    try:
        response = requests.get(f"{API_URL}/chunks/{file_id}")
        if response.status_code == 200:
            chunks = response.json().get("chunks", [])
            if not chunks:
                return "No chunks available."

            # Format chunk preview
            formatted = [
                f"🔹 Chunk {chunk['chunk_number']} (Page {chunk['page_number']}):\n{chunk['text'][:250]}..."
                for chunk in chunks
            ]
            return "\n\n".join(formatted)
    except Exception as e:
        return f"Error loading chunks: {str(e)}"
    
    return "Error fetching chunks."

# ------------------ Ask a Question ------------------

def ask_question(file_id, question):
    """
    Sends a user question to the backend and returns the LLM's answer and source chunks.
    """
    if not file_id:
        return "Please select a file first.", ""
    if not question:
        return "Please enter a question.", ""

    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"file_id": file_id, "question": question, "chat_history": []}
        )
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer found.")
            sources = data.get("sources", [])

            # Format sources
            if sources:
                formatted_sources = [
                    f"🔸 Chunk {s.get('chunk_number')} (Page {s.get('page_number')}):\n{s.get('text')}"
                    for s in sources
                ]
                source_str = "\n\n".join(formatted_sources)
            else:
                source_str = "No source chunks found."

            return answer, source_str
    except Exception as e:
        return f"Error: {str(e)}", ""
    
    return "Error fetching answer.", ""

# ================== Gradio UI ==================

with gr.Blocks() as demo:
    gr.Markdown("# 📄 IntelliDoc QA System")

    # --- Upload Section ---
    with gr.Row():
        file_input = gr.File(label="Upload PDF or Text File")
        upload_btn = gr.Button("Upload")
        status = gr.Textbox(label="Upload Status", interactive=False)

    # --- File Selection and Refresh ---
    with gr.Row():
        file_dropdown = gr.Dropdown(label="Select Uploaded File", choices=[])
        refresh_btn = gr.Button("🔄 Refresh Files")

    # --- Metadata & Summary Display ---
    with gr.Row():
        metadata_output = gr.Textbox(label="📄 Metadata", lines=5, interactive=False)
        summary_output = gr.Textbox(label="📋 Summary", lines=5, interactive=False)

    # --- Chunk Preview Section ---
    with gr.Row():
        chunk_output = gr.Textbox(label="📑 Document Chunks Preview", lines=12, interactive=False)

    # --- Question Input Section ---
    with gr.Row():
        question_input = gr.Textbox(label="💬 Ask a Question")
        ask_btn = gr.Button("Get Answer")

    # --- Answer & Sources Display ---
    with gr.Row():
        answer_output = gr.Textbox(label="🧠 Answer", lines=5, interactive=False)
        source_output = gr.Textbox(label="📌 Cited Chunks", lines=10, interactive=False)

    # === Link Buttons to Functions ===
    upload_btn.click(upload_file, inputs=file_input, outputs=status)
    refresh_btn.click(update_dropdown, outputs=file_dropdown)
    file_dropdown.change(get_summary_and_metadata, inputs=file_dropdown, outputs=[metadata_output, summary_output])
    file_dropdown.change(get_chunks, inputs=file_dropdown, outputs=chunk_output)
    ask_btn.click(ask_question, inputs=[file_dropdown, question_input], outputs=[answer_output, source_output])

demo.launch()

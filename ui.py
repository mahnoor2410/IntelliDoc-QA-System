import gradio as gr
import requests

API_URL = "http://127.0.0.1:5000"

def upload_file(file):
    if not file:
        return "No file selected."
    file_type = "pdf" if file.name.endswith(".pdf") else "text"
    with open(file.name, "rb") as f:
        files = {"file": (file.name, f, f"application/{file_type}")}
        response = requests.post(f"{API_URL}/upload", files=files)
    if response.status_code == 200:
        return response.json().get("message", "Upload succeeded.")
    else:
        return f"Upload failed: {response.text}"

def get_uploaded_files():
    response = requests.get(f"{API_URL}/files")
    if response.status_code == 200:
        files = response.json()  # This should be a list of file IDs (strings)
        return files
    return []

def update_dropdown():
    files = get_uploaded_files()
    return gr.update(choices=files, value=None)

def get_summary_and_metadata(file_id):
    if not file_id:
        return "No file selected.", "No file selected."
    response = requests.get(f"{API_URL}/summary/{file_id}")
    if response.status_code == 200:
        data = response.json()
        metadata = data.get("metadata", "No metadata available.")
        summary = data.get("summary", "No summary available.")
        return metadata, summary
    return "Error fetching metadata.", "Error fetching summary."

def get_chunks(file_id):
    if not file_id:
        return "No file selected."
    response = requests.get(f"{API_URL}/chunks/{file_id}")
    if response.status_code == 200:
        chunks = response.json().get("chunks", [])
        if not chunks:
            return "No chunks available."
        formatted = [f"Chunk {i+1}: {chunk[:200]}..." for i, chunk in enumerate(chunks)]
        return "\n\n".join(formatted)
    return "Error fetching chunks."

def ask_question(file_id, question):
    if not file_id:
        return "Please select a file first.", ""
    if not question:
        return "Please enter a question.", ""
    response = requests.post(f"{API_URL}/ask", json={"file_id": file_id, "question": question, "chat_history": []})
    if response.status_code == 200:
        data = response.json()
        answer = data.get("answer", "No answer found.")
        sources = data.get("sources", [])
        source_str = "\n\n".join([f"Source: {src}" for src in sources]) if sources else "No sources available."
        return answer, source_str
    return "Error fetching answer.", ""

with gr.Blocks() as demo:
    gr.Markdown("# 📄 IntelliDoc QA System")

    with gr.Row():
        file_input = gr.File(label="Upload PDF or Text File")
        upload_btn = gr.Button("Upload")
        status = gr.Textbox(label="Upload Status", interactive=False)

    with gr.Row():
        file_dropdown = gr.Dropdown(label="Select Uploaded File", choices=[])
        refresh_btn = gr.Button("🔄 Refresh Files")

    with gr.Row():
        metadata_output = gr.Textbox(label="Metadata", lines=4, interactive=False)
        summary_output = gr.Textbox(label="Summary", lines=4, interactive=False)

    with gr.Row():
        chunk_output = gr.Textbox(label="Document Chunks Preview", lines=10, interactive=False)

    with gr.Row():
        question_input = gr.Textbox(label="Ask a Question")
        ask_btn = gr.Button("Get Answer")

    with gr.Row():
        answer_output = gr.Textbox(label="Answer", lines=5, interactive=False)
        source_output = gr.Textbox(label="Cited Chunks", lines=6, interactive=False)

    upload_btn.click(upload_file, inputs=file_input, outputs=status)
    refresh_btn.click(update_dropdown, inputs=[], outputs=file_dropdown)
    file_dropdown.change(get_summary_and_metadata, inputs=file_dropdown, outputs=[metadata_output, summary_output])
    file_dropdown.change(get_chunks, inputs=file_dropdown, outputs=chunk_output)
    ask_btn.click(ask_question, inputs=[file_dropdown, question_input], outputs=[answer_output, source_output])

demo.launch()

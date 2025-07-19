
# 📄 IntelliDoc QA System

**IntelliDoc QA System is a multi-document RAG-based chatbot using LangChain and Google Gemini. It lets users upload PDFs or text, view chunked previews, get smart summaries, and ask context-aware questions with citations — all in an interactive Gradio UI.

Built with 🐍 Flask and Gradio, and integrated with 🧠 FAISS and 🤗 HuggingFace embeddings, the system delivers accurate, explainable, and responsive document understanding — ideal for 📚 legal, 🏫 academic, and 🏢 business workflows.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Authors](#authors)
- [Acknowledgments](#acknowledgments)

---

## Project Overview

Manual document reading and context extraction is time-consuming and error-prone. **IntelliDoc QA System** transforms this experience by enabling real-time question-answering across uploaded documents with cited context chunks and memory tracking.

This AI-powered system allows users to upload and query multiple PDFs or text files with summaries, chunk visualizations, and intelligent responses — all using Gemini LLM via LangChain. It is scalable, user-friendly, and fully modular for future expansion.

---

## Features

- 📂 **Multi-File Upload Support**: Upload multiple `.pdf` or `.txt` files.
- 🧠 **Semantic Chunking & Storage**: Uses `RecursiveCharacterTextSplitter` + FAISS.
- 📑 **AI-Powered Summary Generator**: Two-paragraph smart summaries from Gemini.
- ❓ **Question Answering**: Ask anything — get accurate, cited responses.
- 🧷 **Citation & Chunk Preview**: Sources included with clickable context.
- 💾 **Memory Tracking**: Keeps chat history per session & file.
- 🔗 **Flask Backend API**: RESTful endpoints for upload, QA, chunks & summaries.
- 🧑‍💻 **Gradio Frontend**: UI with dropdowns, previews, and real-time answers.

---

## Tech Stack

- **Backend**: Python, Flask, Flask-CORS
- **Frontend**: Gradio (Blocks API)
- **LLM**: Gemini 1.5 Flash via `langchain-google-genai`
- **Embeddings**: HuggingFace MiniLM (`sentence-transformers/all-MiniLM-L6-v2`)
- **Vector Store**: FAISS
- **Text Splitting**: RecursiveCharacterTextSplitter (LangChain)
- **Document Loaders**: `PyPDFLoader`, `TextLoader` from `langchain_community`
- **Environment Management**: `dotenv`, `.env`

---

## System Architecture

- **🔁 Upload & Process**:
  1. User uploads a document via Gradio frontend.
  2. File saved locally, then parsed into text.
  3. Document is split into chunks and vectorized using embeddings.
  4. Stored as FAISS index under a `file_id`.

- **🧠 Summarization**:
  - Gemini model is prompted to summarize top `k=100` relevant chunks using custom prompt.

- **🔍 Question Answering**:
  - Gemini uses RetrievalQA chain to answer using top 4 similar chunks.
  - Citations and chat history returned.

- **🎛️ Frontend Interaction**:
  - Gradio dropdown to switch between uploaded documents.
  - Summary, metadata, chunk preview, and question-answer interface.

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- Google API Key with access to Gemini
- FAISS
- PyPDF2 or pdfminer.six
- Gradio
- dotenv

### Installation

1. **Clone the Repository**

```bash
git clone https://github.com/your-username/intellidoc-qa-system.git
cd intellidoc-qa-system
```

2. **Create and Activate Virtual Environment**

```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# source venv/bin/activate    # On macOS/Linux
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Add Environment Variables**

Create a `.env` file:

```env
GOOGLE_API_KEY=your_gemini_api_key
```

5. **Run Backend (Flask Server)**

```bash
python app.py
```

6. **Run Frontend (Gradio UI)**

```bash
python ui.py
```

---

## Usage

- Visit `http://127.0.0.1:7860/` to open the Gradio UI.
- Upload a `.pdf` or `.txt` file.
- Click "Refresh Files" to populate the dropdown.
- Select a file to:
  - View metadata
  - See the AI-generated summary
  - Preview the document chunks
- Ask any question about the selected document.
- View the AI-generated answer with source chunks.

---

## Screenshots

> *(Replace the placeholders below with your actual Gradio UI screenshots once available)*

![Upload File & Status](https://your-image-link.com/upload.png)

![File Summary & Metadata](https://your-image-link.com/summary.png)

![Chunk Preview](https://your-image-link.com/chunks.png)

![Ask Question](https://your-image-link.com/qa.png)

![Cited Answer](https://your-image-link.com/answer_sources.png)

---

## Contributing

Contributions are welcome!

1. Fork this repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit your changes.
4. Push to your branch: `git push origin feature/your-feature`.
5. Submit a Pull Request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

## Authors

- Mahnoor Shahid

---

## Acknowledgments

- [LangChain](https://www.langchain.com/)
- [Google Gemini](https://deepmind.google/technologies/gemini/)
- [Gradio](https://www.gradio.app/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [HuggingFace Embeddings](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)



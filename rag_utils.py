import os
from datetime import datetime
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from dotenv import load_dotenv

load_dotenv()

# Define directories for database and uploaded files
DB_DIR = "db"
UPLOAD_DIR = "uploaded_files"
os.makedirs(DB_DIR, exist_ok=True)

# Initialize embedding model
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize LLM using Google Gemini (via API key)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3
)

# Define prompt structure for QA task
prompt_template = """Use the context to answer the question.
Context: {context}
Question: {question}
Answer:"""
prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

# ------------------ PDF Processing & Storage ------------------

def process_and_store_pdf(file_path):
    """
    Loads and splits a PDF file into chunks, then stores them in a FAISS vector database.
    """
    file_id = os.path.splitext(os.path.basename(file_path))[0]
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Tag each page with its page number
    for i, doc in enumerate(documents):
        doc.metadata["page_number"] = i + 1

    # Split content into overlapping chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    # Add chunk number metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_number"] = i

    # Store in FAISS vector DB
    db = FAISS.from_documents(chunks, embedding)
    db.save_local(os.path.join(DB_DIR, file_id))

# ------------------ List Uploaded Files ------------------

def get_uploaded_files():
    """
    Returns a list of all uploaded file directories (vector DB folders).
    """
    return [f for f in os.listdir(DB_DIR) if os.path.isdir(os.path.join(DB_DIR, f))]

# ------------------ Get Chunks for Summary or Display ------------------

def get_chunks_for_file(file_id, n=10):
    """
    Returns the top N chunks from a given file for display or summarization.
    """
    path = os.path.join(DB_DIR, file_id)
    if not os.path.exists(path):
        return []

    db = FAISS.load_local(path, embeddings=embedding, allow_dangerous_deserialization=True)
    docs = db.similarity_search(" ", k=n)

    chunk_data = []
    for doc in docs:
        chunk_data.append({
            "chunk_number": doc.metadata.get("chunk_number"),
            "page_number": doc.metadata.get("page_number"),
            "text": doc.page_content
        })

    return chunk_data

# ------------------ Summarization ------------------

def get_summary_for_file(file_id):
    """
    Generates a summary of the document using selected chunks and the LLM.
    """
    chunks = get_chunks_for_file(file_id, n=12)
    if not chunks:
        return "No summary available."

    docs = [Document(page_content=chunk["text"]) for chunk in chunks]
    chain = load_summarize_chain(llm, chain_type="map_reduce")

    try:
        summary = chain.run(docs)
        return summary
    except Exception as e:
        return f"Summary generation error: {str(e)}"

# ------------------ Metadata Retrieval ------------------

def get_metadata_for_file(file_id):
    """
    Returns metadata such as page count, size, and upload time for a given file.
    """
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    try:
        # Read PDF and extract metadata
        reader = PdfReader(file_path)
        num_pages = len(reader.pages)

        stats = os.stat(file_path)
        file_size_kb = round(stats.st_size / 1024, 2)
        upload_date = datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S")

        return {
            "file_name": f"{file_id}.pdf",
            "file_type": ".pdf",
            "page_count": num_pages,
            "upload_date": upload_date,
            "file_size_kb": file_size_kb
        }

    except Exception as e:
        return {"error": str(e)}

# ------------------ Q&A Functionality ------------------

def get_answer(file_id, question, chat_history):
    """
    Returns an answer to a question based on the content of the specified file.
    Also returns the source chunks and updated chat history.
    """
    path = os.path.join(DB_DIR, file_id)
    if not os.path.exists(path):
        return "File not found.", [], chat_history

    db = FAISS.load_local(path, embeddings=embedding, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    result = qa_chain({"query": question})
    answer = result["result"]

    # Collect metadata about the answer's sources
    source_chunks = []
    for doc in result["source_documents"]:
        source_chunks.append({
            "chunk_number": doc.metadata.get("chunk_number"),
            "page_number": doc.metadata.get("page_number"),
            "text": doc.page_content[:300] + "..."  # Preview of the chunk
        })

    updated_history = chat_history + [(question, answer)]
    return answer, source_chunks, updated_history

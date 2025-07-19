import os
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

DB_DIR = "db"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3
)

prompt_template = """Use the context to answer the question.
Context: {context}
Question: {question}
Answer:"""
prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

def process_and_store_pdf(file_path):
    file_id = os.path.splitext(os.path.basename(file_path))[0]
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    db = FAISS.from_documents(chunks, embedding)
    db.save_local(os.path.join(DB_DIR, file_id))

def get_uploaded_files():
    # Return list of folder names (= file_ids) in DB_DIR
    return [f for f in os.listdir(DB_DIR) if os.path.isdir(os.path.join(DB_DIR, f))]

def get_chunks_for_file(file_id):
    path = os.path.join(DB_DIR, file_id)
    if not os.path.exists(path):
        return []

    db = FAISS.load_local(path, embeddings=embedding, allow_dangerous_deserialization=True)
    docs = db.similarity_search(" ", k=10)
    return [doc.page_content for doc in docs]

def get_summary_for_file(file_id):
    chunks = get_chunks_for_file(file_id)
    if not chunks:
        return "No summary available."

    docs = [Document(page_content=chunk) for chunk in chunks]

    # Load map_reduce summarize chain for hierarchical summarization
    chain = load_summarize_chain(llm, chain_type="map_reduce")

    try:
        summary = chain.run(docs)
        return summary
    except Exception as e:
        return f"Summary generation error: {str(e)}"

def get_answer(file_id, question, chat_history):
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
    sources = list({doc.metadata.get("source", "Unknown") for doc in result["source_documents"]})
    updated_history = chat_history + [(question, answer)]
    return answer, sources, updated_history

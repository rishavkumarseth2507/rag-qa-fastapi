from dotenv import load_dotenv
load_dotenv()

import os
import json
import time
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS


# -------------------- basic setup --------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
VECTOR_DIR = DATA_DIR / "vectorstores"
REGISTRY_PATH = DATA_DIR / "registry.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 4
MAX_FILE_SIZE_MB = 15
ALLOWED_EXTENSIONS = {".pdf", ".txt"}

embedding_model = "gemini-embedding-001"
primary_model = "llama-3.3-70b-versatile"
secondary_model = "llama-3.1-8b-instant"

prompt = """
You are a document question-answering assistant.

Use only the retrieved document context to answer.
If the answer is not available in the context, reply exactly:
Not found in document.

Keep the answer short and clear.
Add page references like [Page X] whenever possible.
"""

# -------------------- app --------------------
app = FastAPI(
    title="RAG QA API",
    version="1.0.0",
    description="Upload documents and ask questions from them"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# -------------------- request/response models --------------------
class UploadResponse(BaseModel):
    message: str
    doc_id: str
    status: str
    filename: str

class StatusResponse(BaseModel):
    doc_id: str
    filename: str
    status: str
    file_type: str
    total_chunks: int = 0
    error: Optional[str] = None

class AskRequest(BaseModel):
    doc_id: str = Field(..., description="Document id returned during upload")
    question: str = Field(..., min_length=3, max_length=2000)

class SourceChunk(BaseModel):
    page: str
    content: str

class AskResponse(BaseModel):
    doc_id: str
    question: str
    answer: str
    retrieval_latency_ms: float
    total_retrieved_chunks: int
    sources: List[SourceChunk]


# -------------------- small helpers --------------------
def ensure_registry():
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.write_text("{}", encoding="utf-8")

def read_registry():
    ensure_registry()
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def write_registry(data):
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_doc_record(doc_id, record):
    data = read_registry()
    data[doc_id] = record
    write_registry(data)

def update_doc_record(doc_id, updates):
    data = read_registry()
    if doc_id in data:
        data[doc_id].update(updates)
        write_registry(data)

def get_doc_record(doc_id):
    data = read_registry()
    return data.get(doc_id)

def make_doc_id():
    return str(uuid.uuid4())

def get_file_ext(filename: str):
    return Path(filename).suffix.lower()

def clean_filename(filename: str):
    return os.path.basename(filename).replace(" ", "_")

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model=embedding_model)

def get_llm():
    try:
        return ChatGroq(model=primary_model, streaming=False)
    except Exception:
        return ChatGroq(model=secondary_model, streaming=False)


# -------------------- ingestion --------------------
def load_file(file_path: str):
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        loader = PyPDFLoader(str(path))
        docs = loader.load()

    elif ext == ".txt":
        loader = TextLoader(str(path), encoding="utf-8")
        docs = loader.load()

        # txt has no page number, so add a simple label
        for doc in docs:
            doc.metadata["page"] = "TXT"

    else:
        raise ValueError("Unsupported file format")

    return docs

def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_documents(docs)

def save_vectorstore(docs, save_path: str):
    embeddings = get_embeddings()
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(save_path)

def process_document(doc_id: str, file_path: str):
    try:
        update_doc_record(doc_id, {"status": "processing", "error": None})

        raw_docs = load_file(file_path)
        chunks = split_docs(raw_docs)

        vector_path = str(VECTOR_DIR / doc_id)
        save_vectorstore(chunks, vector_path)

        update_doc_record(
            doc_id,
            {
                "status": "ready",
                "total_chunks": len(chunks),
                "vectorstore_path": vector_path,
            }
        )
    except Exception as e:
        update_doc_record(
            doc_id,
            {
                "status": "failed",
                "error": str(e),
            }
        )


# -------------------- retrieval --------------------
def load_saved_vectorstore(vectorstore_path: str):
    embeddings = get_embeddings()
    db = FAISS.load_local(
        vectorstore_path,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return db

def get_relevant_chunks(vectorstore_path: str, query: str, top_k: int = TOP_K):
    db = load_saved_vectorstore(vectorstore_path)

    start = time.perf_counter()
    docs = db.similarity_search(query=query, k=top_k)
    end = time.perf_counter()

    latency_ms = round((end - start) * 1000, 2)
    return docs, latency_ms

def build_answer(question: str, docs):
    if not docs:
        return "Not found in document."

    parts = []
    for doc in docs:
        page = doc.metadata.get("page", "unknown")
        text = doc.page_content.strip()
        parts.append(f"[Page {page}] {text}")

    context = "\n\n".join(parts)

    final_prompt = f"""
                        {prompt}

                        Context:
                        {context}

                        Question:
                        {question}
                    """

    llm = get_llm()
    response = llm.invoke(final_prompt)
    if hasattr(response, "content"):
        return response.content.strip()
    return str(response).strip()


# -------------------- routes --------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload", response_model=UploadResponse)
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    ext = get_file_ext(file.filename)

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max allowed size is {MAX_FILE_SIZE_MB} MB"
        )

    doc_id = make_doc_id()
    filename = clean_filename(file.filename)
    saved_path = UPLOAD_DIR / f"{doc_id}_{filename}"

    with open(saved_path, "wb") as f:
        f.write(content)

    file_type = ext.replace(".", "").upper()
    add_doc_record(
        doc_id,
        {
            "doc_id": doc_id,
            "filename": filename,
            "file_path": str(saved_path),
            "file_type": file_type,
            "status": "queued",
            "total_chunks": 0,
            "vectorstore_path": "",
            "error": None,
        }
    )

    background_tasks.add_task(process_document, doc_id, str(saved_path))
    return UploadResponse(
        message="File uploaded successfully. Processing started in background.",
        doc_id=doc_id,
        status="queued",
        filename=filename
    )

@app.get("/status/{doc_id}", response_model=StatusResponse)
def check_status(doc_id: str):
    doc = get_doc_record(doc_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return StatusResponse(
        doc_id=doc["doc_id"],
        filename=doc["filename"],
        status=doc["status"],
        file_type=doc["file_type"],
        total_chunks=doc.get("total_chunks", 0),
        error=doc.get("error"),
    )

@app.post("/ask", response_model=AskResponse)
@limiter.limit("5/minute")
def ask_question(request: Request, payload: AskRequest):
    doc = get_doc_record(payload.doc_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc["status"] != "ready":
        raise HTTPException(
            status_code=400,
            detail=f"Document is not ready yet. Current status: {doc['status']}"
        )

    retrieved_docs, latency_ms = get_relevant_chunks(
        vectorstore_path=doc["vectorstore_path"],
        query=payload.question,
        top_k=TOP_K
    )

    answer = build_answer(payload.question, retrieved_docs)
    sources = []
    for item in retrieved_docs:
        page = str(item.metadata.get("page", "unknown"))
        text = item.page_content.strip()
        sources.append(
            SourceChunk(
                page=page,
                content=text[:500]
            )
        )

    return AskResponse(
        doc_id=payload.doc_id,
        question=payload.question,
        answer=answer,
        retrieval_latency_ms=latency_ms,
        total_retrieved_chunks=len(retrieved_docs),
        sources=sources
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
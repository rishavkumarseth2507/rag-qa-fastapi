# 🚀 RAG-Based Question Answering System (FastAPI)

A production-style Retrieval-Augmented Generation (RAG) API that allows users to upload documents and ask context-aware questions using embeddings, vector search, and LLMs.

---

## 🎥 Demo Video

This demo shows the complete RAG pipeline:
**document upload → background ingestion → embeddings → retrieval → LLM answer generation**

[![Watch Demo](https://img.youtube.com/vi/3-8h5HIcPsE/0.jpg)](https://youtu.be/3-8h5HIcPsE)

---

## ✨ Features

- 📄 Supports **PDF and TXT** document upload  
- ✂️ Intelligent **document chunking (1000 size, 200 overlap)**  
- 🔍 **Semantic search** using FAISS vector database  
- 🤖 Answer generation using **Groq LLM (LLaMA models)**  
- ⚡ **FastAPI backend** with clean API design  
- 🔄 **Background ingestion pipeline** (non-blocking)  
- 📊 Tracks **retrieval latency**  
- 🚫 **Rate limiting** (5 requests/minute)  
- 🧾 Structured responses with **source references**

---

## 🧠 Tech Stack

- **Backend:** FastAPI  
- **Embeddings:** Google Generative AI (`gemini-embedding-001`)  
- **Vector Store:** FAISS  
- **LLM:** Groq (`llama-3.3-70b-versatile`, fallback supported)  
- **Chunking:** RecursiveCharacterTextSplitter  
- **Rate Limiting:** slowapi  

---

## 🏗️ Architecture Flow
User → FastAPI API

/upload → Save file → Background ingestion
→ Chunking → Embeddings → FAISS storage

/ask → Load FAISS → Similarity search (Top-K)
→ Context building → LLM → Answer + sources + latency



---
## Project Structure

```bash
rag_fastapi/
│
├── main.py
├── data/
├── requirements.txt
├── .env.example
├── README.md
└── explanation.md
```

---
## Tech Stack
- Backend: FastAPI
- Embeddings: Google Generative AI Embeddings (gemini-embedding-001)
- Vector Store: FAISS
- LLM: Groq (llama-3.3-70b-versatile, fallback: llama-3.1-8b-instant)
- Document Parsing: PyPDFLoader, TextLoader
- Rate Limiting: slowapi


---
## Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone <your-github-repo-link>
cd rag_fastapi
```


### 2️⃣ Create virtual environment

```bash
python -m venv myenv
myenv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup environment variables

```bash
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
```

### 5️⃣ Run the server

```bash
uvicorn main:app --reload
```


### 6️⃣ Open API Docs
```bash
👉 http://127.0.0.1:8000/docs
```

------

## 📡 API Endpoints
### 📤 Upload Document
```bash
POST /upload
```
- Upload PDF or TXT file
- Returns doc_id

### 📊 Check Status
```bash
GET /status/{doc_id}
```
- Check processing status
- Returns number of chunks

### ❓ Ask Question
```bash
POST /ask
```

Request:
```bash
{
  "doc_id": "your_doc_id",
  "question": "Your question here"
}
```

Response:
```bash
{
  "answer": "...",
  "retrieval_latency_ms": 12.5,
  "sources": [...]
}
```
-----
📊 Metrics Tracked
- Retrieval latency (ms)
- Number of retrieved chunks





------
## ⚠️ Limitations
- Only supports PDF and TXT files
- Single document querying (per doc_id)
- No hybrid search (only embeddings)


## 🔍 Key Design Decisions
- Used FAISS for fast local retrieval
- Implemented background tasks to avoid blocking API
- Used chunk size = 1000, overlap = 200 for balance between context and precision
- Strict prompt to prevent hallucination

## 🚀 Future Improvements
- Hybrid search (BM25 + embeddings)
- Reranking models
- Multi-document querying
- Streaming responses

## 👨‍💻 Author

Rishav Kumar
MSc Mathematics & Scientific Computing, MNNIT Allahabad
Aspiring AI/ML & LLM Engineer


⭐ If you found this useful
Give a ⭐ to the repository!

# RAG-Based Question Answering System

A FastAPI-based Retrieval-Augmented Generation (RAG) system that allows users to upload documents and ask questions grounded in those documents.

## Features

- Upload documents in **PDF** and **TXT** formats
- Background document ingestion
- Document chunking using `RecursiveCharacterTextSplitter`
- Embedding generation using **Google Generative AI Embeddings**
- Local vector storage using **FAISS**
- Similarity-based retrieval
- Answer generation using **Groq LLM**
- Request validation using **Pydantic**
- Basic API rate limiting using **slowapi**
- Retrieval latency tracking

---
## 📌 Features

- 📄 Supports **PDF and TXT** document upload
- ✂️ Intelligent **document chunking**
- 🔍 **Semantic search** using FAISS vector database
- 🤖 Answer generation using **LLMs (Groq - LLaMA models)**
- ⚡ **FastAPI backend** with clean API design
- 🔄 **Background processing** for document ingestion
- 📊 Tracks **retrieval latency**
- 🚫 **Rate limiting** to prevent abuse
- 🧾 Structured responses with **source references**

---
## 🧠 Tech Stack

- **Backend:** FastAPI
- **Embeddings:** Google Generative AI (`gemini-embedding-001`)
- **Vector Store:** FAISS
- **LLM:** Groq (LLaMA models)
- **Chunking:** RecursiveCharacterTextSplitter
- **Rate Limiting:** slowapi

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

```

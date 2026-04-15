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

## Project Structure

```bash
rag_fastapi/
│
├── main.py
├── data/
│   ├── uploads/
│   ├── vectorstores/
│   └── registry.json
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
1. Clone the repository
```bash
git clone <your-github-repo-link>
cd rag_fastapi
```


2. Create virtual environment
Windows
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```



```bash

```



```bash

```



```bash

```



```bash

```



```bash

```



```bash

```

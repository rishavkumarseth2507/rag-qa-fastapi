# RAG-Based Question Answering System – Explanation

## 1. Overview

This project implements a Retrieval-Augmented Generation (RAG) based API using FastAPI.  
The system allows users to upload documents (PDF/TXT), processes them into embeddings, stores them in a vector database, and enables question answering using an LLM.

The pipeline follows:

Upload → Chunking → Embedding → Vector Store → Retrieval → LLM Answer Generation

---

## 2. Chunking Strategy

### Configuration used:
- Chunk Size: 1000 characters
- Chunk Overlap: 200 characters

### Why this choice?

- A chunk size of **1000** provides enough context for the LLM to understand meaningful content without being too large.
- Smaller chunks (like 200–300) often lose context.
- Larger chunks (>1500) increase noise and reduce retrieval precision.
- Overlap of **200** ensures:
  - Continuity of information across chunks
  - Avoids breaking important sentences or concepts

### Trade-off:
- Larger chunk → better context but worse retrieval precision  
- Smaller chunk → better retrieval but weaker context  

So, 1000/200 is a balanced configuration.

---

## 3. Retrieval Mechanism

- Vector store: **FAISS (local storage)**
- Embedding model: `gemini-embedding-001`
- Retrieval method: similarity search
- Top-K chunks: 4

### Why FAISS?

- Fast and efficient for local similarity search
- No external dependency (unlike Pinecone)
- Suitable for small-to-medium scale systems

---

## 4. Background Processing

Document ingestion is handled using FastAPI BackgroundTasks.

### Why?

- Upload endpoint returns immediately (non-blocking)
- Large files don't block API responsiveness
- Improves user experience

Pipeline:
1. File uploaded → status = queued
2. Background job starts
3. Processing:
   - Load file
   - Chunking
   - Embedding
   - Store in FAISS
4. Status updated to "ready"

---

## 5. Retrieval Failure Case

### Observed Issue:

When the user asks a **very generic or abstract question**, retrieval sometimes fails.

#### Example:
Question:
> "What is the main idea?"

Problem:
- Query is too vague
- Similarity search cannot match specific chunks
- Returns irrelevant or weak context

### Why it happens:
- Embedding-based retrieval depends on semantic similarity
- Vague queries don't map strongly to specific vectors

### Mitigation:
- Encourage specific queries
- Could improve using:
  - Query rewriting
  - Hybrid search (keyword + embedding)
  - Reranking models

---

## 6. Metric Tracked

### Retrieval Latency

We tracked:
- **Time taken for similarity search (in milliseconds)**

Why this metric?

- Helps measure system performance
- Important for real-time applications
- Indicates scalability issues

### Observation:
- FAISS retrieval is very fast (<50 ms in most cases)
- Latency increases slightly with larger vector stores

---

## 7. API Design Decisions

### Endpoints:

- `/upload` → Upload document
- `/status/{doc_id}` → Check processing status
- `/ask` → Ask question

### Design choices:

- UUID-based document tracking
- Registry (JSON file) for metadata storage
- Background ingestion pipeline
- Structured request/response using Pydantic

---

## 8. Rate Limiting

- Implemented using `slowapi`
- Limit: 5 requests per minute on `/ask`

### Why?

- Prevent API abuse
- Control LLM usage cost
- Ensure fair usage

---

## 9. LLM Selection Strategy

Primary model:
- `llama-3.3-70b-versatile`

Fallback model:
- `llama-3.1-8b-instant`

### Why fallback?

- Improves reliability
- Handles API/model failures gracefully

---

## 10. Prompt Design

The system uses a **strict grounding prompt**:

- Only answer from provided context
- If answer not found → return:
  "Not found in document"

### Why?

- Prevent hallucination
- Ensure factual answers
- Improve trustworthiness

---

## 11. Limitations

- No hybrid search (only embeddings)
- No reranking layer
- Limited to PDF/TXT
- No multi-document querying (per doc_id only)

---

## 12. Possible Improvements

- Add BM25 + embedding hybrid search
- Add reranker (Cross-Encoder)
- Add streaming responses
- Add multi-document querying
- Replace JSON registry with database

---

## 13. Conclusion

This system demonstrates a complete RAG pipeline with:

- Efficient chunking strategy
- Fast similarity retrieval
- Background processing
- Clean API design
- Basic production considerations (rate limiting, validation)

It balances simplicity and performance, making it suitable for real-world applications at small-to-medium scale.
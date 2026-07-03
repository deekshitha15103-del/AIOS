# 🤖 AIOS – Enterprise AI Knowledge Assistant

AIOS is a production-style Retrieval-Augmented Generation (RAG) system that allows users to upload PDF documents and ask natural language questions with cited answers.

Unlike simple chatbot demos, AIOS implements an end-to-end enterprise document intelligence pipeline including document ingestion, semantic search, hybrid retrieval, conversation memory, and source-grounded responses.

---

# Features

- PDF Upload
- Automatic Text Extraction
- Intelligent Chunking
- Sentence Transformer Embeddings
- FAISS Vector Search
- BM25 Keyword Search
- Hybrid Retrieval
- Multi-document Support
- Conversation Memory
- Source Citations
- FastAPI REST API
- Streamlit Frontend
- Ollama (Llama 3.2)

---

# Architecture

```text
                PDF Upload
                     │
                     ▼
            Document Processor
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
 Text Extraction   Chunking     Metadata
                     │
                     ▼
          Sentence Transformer
                     │
                     ▼
              Vector Embeddings
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
      FAISS                    BM25
        └────────────┬────────────┘
                     ▼
             Hybrid Retrieval
                     ▼
           Conversation Memory
                     ▼
             Ollama (Llama 3.2)
                     ▼
            Response Generation
                     ▼
               Streamlit UI
```

---

# Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn

### AI

- Ollama
- Llama 3.2
- Sentence Transformers
- FAISS
- BM25

### Frontend

- Streamlit

### Document Processing

- PyPDF

---

# Project Structure

```
backend/
frontend/
data/
assets/

Dockerfile
docker-compose.yml
requirements.txt
README.md
```

---

# Running Locally

Backend

```bash
uvicorn backend.main:app --reload
```

Frontend

```bash
streamlit run frontend/app.py
```

---

# Example Workflow

1. Upload a PDF

2. Document is processed automatically

- Text Extraction
- Chunking
- Embeddings
- FAISS Index

3. Ask questions

Example:

```
What is Vijayanagara?
```

AIOS retrieves relevant chunks before generating a grounded answer.

---

# Future Improvements

- Streaming Responses
- Authentication
- Multi-user Support
- PostgreSQL Metadata Store
- Cloud Deployment
- Reranking
- Evaluation Dashboard

---

# Author

**S.R. Deekshitha**

B.Tech Computer Science Engineering

AI & Machine Learning

Interested in:

- Retrieval-Augmented Generation
- LLM Engineering
- Enterprise AI
- Applied Machine Learning
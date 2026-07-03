AIOS: A Local, Hybrid RAG Application
I built AIOS to get my hands dirty with the actual engineering side of production AI applications, moving past simple API wrappers. It’s a local, enterprise-grade Retrieval-Augmented Generation (RAG) system that lets you drop in PDFs and have grounded, natural language conversations with your data.

Instead of just tossing text at an LLM, this project focuses heavily on the mechanics of ingestion, chunking strategies, and balancing semantic depth with exact keyword matching using a custom hybrid retrieval pipeline.

 What it Does
Smart Ingestion: Automatically parses, cleans, and chunks uploaded PDFs.

Hybrid Retrieval: Fuses semantic search (FAISS + Sentence Transformers) with traditional keyword search (BM25) to make sure the LLM actually gets the right context.

100% Local Inference: Runs entirely on your machine using Ollama (Llama 3.2)—no data leaves your local environment, and no API keys are required.

Citational Grounding: Responses aren't just generated out of thin air; the app explicitly surfaces the source chunks used to build the answer.

Session Memory: Keeps track of chat history using session IDs for continuous conversations.

Clean Architecture: Built with a decoupled FastAPI backend and a lightweight Streamlit UI, all ready to be containerized via Docker.

 How it Works under the Hood
The data pipeline follows a classic modular architecture:

[Upload PDF] ➔ [PyPDF Extraction] ➔ [Text Cleaning & Chunking]
                                               │
                    ┌──────────────────────────┴──────────────────────────┐
                    ▼                                                     ▼
     [Vector Embeddings Generator]                                 [Tokenization]
                    │                                                     │
                    ▼                                                     ▼
         [FAISS Index (Semantic)]                             [BM25 Index (Keyword)]
                    │                                                     │
                    └──────────────────────────┬──────────────────────────┘
                                               ▼
                                    [Hybrid Rank Fusion]
                                               │
                                               ▼
                             [Top-K Context + Llama 3.2 via Ollama] ➔ [Grounded Response]
Ingestion & Processing: The PDF is stripped to raw text via PyPDF, cleaned of formatting artifacts, and broken into overlapping chunks to preserve context at the boundaries.

Dual-Indexing: Chunks are simultaneously vectorized using all-MiniLM-L6-v2 for the FAISS vector store and tokenized for the BM25 keyword index.

Query & Fusion: When you ask a question, AIOS hits both indexes. Semantic search catches the conceptual meaning, while BM25 catches exact IDs, names, or specific terminology. The results are merged to pull the absolute best reference text.

Generation: The final context window is structured and sent to Llama 3.2, yielding a response tied directly to your document.

 Tech Stack
Core: Python 3.11

API & Backend: FastAPI (REST)

UI Frontend: Streamlit

Local LLM Orchestration: Ollama (Llama 3.2)

Vector Embeddings: Sentence Transformers (all-MiniLM-L6-v2)

Vector Database: FAISS

Keyword Search: BM25

Deployment: Docker / Docker Compose

Project Structure
Plaintext
AIOS/
├── assets/             # Graphics and UI elements
├── backend/            # The heavy lifting
│   ├── api/            # FastAPI endpoints & routers
│   ├── core/           # LLM orchestration & RAG pipeline logic
│   ├── modules/        # Chunking, embedding, and indexing engines
│   └── schemas/        # Pydantic data models
├── data/               # Local storage for uploads and index files
├── docs/               # Architecture notes
├── frontend/           # Streamlit interface
│   └── app.py
├── scripts/            # Utility and setup scripts
├── tests/              # Unit and integration tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── start_aios.ps1       # One-click bootstrap script
 Getting Started
1. Clone & Navigate
Bash
git clone https://github.com/<your-username>/AIOS.git
cd AIOS
2. Environment Setup
Set up a clean virtual environment to keep dependencies isolated:

Windows:

PowerShell
python -m venv venv
.\venv\Scripts\activate
Linux/macOS:

Bash
python3 -m venv venv
source venv/bin/activate
Install the dependencies:

Bash
pip install -r requirements.txt
3. Spin up the Local LLM
Make sure you have Ollama installed on your system, then pull the model weights and start the engine:

Bash
# Pull Llama 3.2
ollama pull llama3.2

# Fire up the local server
ollama serve
4. Run the App
If you are on Windows, you can use the automation script to launch everything at once:

PowerShell
.\start_aios.ps1
Otherwise, pull open two terminal tabs to run the services independently:

Tab 1 (Backend):

Bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
Tab 2 (Frontend):

Bash
streamlit run frontend/app.py
Once up, open your browser to the local Streamlit address (usually http://localhost:8501), drop in a document, and start testing the retrieval performance!
Using the App
Once your backend, frontend, and Ollama are up and running, head over to the Streamlit local URL in your browser. The loop is straightforward:

Drop your PDF into the upload zone.

Wait a brief moment while the background pipeline handles the parsing and indexing.

Start chatting naturally with your document.

Verify the outputs by checking the interactive source blocks that reveal exactly which pages or text sections the model used.

 Deep Dive: Under the Hood
While the UI keeps things simple, there's a lot moving under the surface to prevent the LLM from hallucinating or losing context.

Ingestion & Optimization
The preprocessing pipeline runs exactly once per document upload. It isn't just dumping raw text into a database; it strips junk whitespace, normalizes formatting artifacts, and applies an overlapping character split strategy. This keeps important concepts from getting sliced in half right at a chunk boundary.

The Power of Hybrid Retrieval
RAG systems often struggle if they rely entirely on vector math. Pure semantic search (FAISS) is incredible at capturing conceptual context, but it frequently whiffs on specific nouns, exact version numbers, or rare terminology.

To fix this, AIOS uses Reciprocal Rank Fusion (RRF) to combine semantic scores with BM25 keyword search.

BM25 acts as a safety net for exact matches (like looking for a specific project name, error code, or ID).

FAISS catches the intent when you phrase a question using completely different vocabulary than the document.

Context Engineering & Prompt Construction
Instead of overloading Llama 3.2 with a massive, unfiltered wall of text, AIOS dynamically compiles a highly structured prompt context window containing:

Short-term dialogue history (tracked via your session_id).

Strict behavioral instructions forcing the model to stay grounded.

The precise Top-K relevant document fragments.

This keeps inference lightweight, rapid, and tightly bounded to facts.

Transparent Citations
To move away from the "black box" nature of typical AI tools, every response explicitly links back to its underlying raw data. You can expand the source cards to view the direct chunk snippet, its collection index, and the mathematical confidence score behind the retrieval.

 API Reference
AIOS exposes its entire RAG pipeline through clean FastAPI REST endpoints, making it simple to bypass the Streamlit UI entirely and integrate it into other workflows.

1. Index a Document
HTTP
POST /api/v1/knowledge/documents/upload
Accepts a multipart form PDF upload, kicks off the extraction worker, builds your vector/keyword structures, and registers the document ID.

2. Query the Engine
HTTP
POST /api/v1/knowledge/ask
Executes the hybrid search strategy and passes the context to the local model instance.

Example Request payload:

JSON
{
  "session_id": "dev-sandbox-session",
  "document_id": "project-spec-v2",
  "question": "What core tech stack constraints are outlined?",
  "top_k": 3
}
Example Response payload:

JSON
{
  "success": true,
  "message": "Answer generated successfully",
  "data": {
    "answer": "The project specifies a strict local runtime using Python 3.11 and Ollama for isolated model execution.",
    "sources": [
      {
        "chunk_index": 14,
        "score": 0.8842
      }
    ]
  }
}
 Interface Preview
Here is a quick look at the system UI and API sandbox:

Main Dashboard
Document Ingestion Worker
Contextual Chat Mode
Source Attribution Logs
Interactive OpenAPI Documentation
Architecture & Design Choices
Every component in AIOS was selected to keep the system fast, modular, and completely self-contained on a local machine. Here is the reasoning behind the core architecture:

FastAPI: Serves as a lightweight, high-performance async backend. It gives us out-of-the-box data validation via Pydantic and generates interactive OpenAPI/Swagger docs automatically, which keeps API development smooth.

Streamlit: Chosen purely for speed of execution on the frontend. Utilizing Streamlit meant zero time wasted on boilerplate UI/UX, letting the focus stay entirely on refining the core RAG logic and indexing pipeline.

FAISS: A highly efficient vector similarity library that delivers lightning-fast semantic retrieval. It keeps the deployment footprint incredibly light by running entirely in-memory without requiring a heavyweight external cluster.

BM25: Vector math can easily look past specific identifiers, alpha-numeric serial numbers, proper nouns, or exact terminology. BM25 acts as a deterministic keyword safety net, catching the exact phrases that vector embeddings might compress away.

Ollama (Llama 3.2): Keeping inference local guarantees absolute data privacy, removes network latency bottlenecks, eliminates unpredictable commercial API costs, and lets the entire system run completely offline.

Performance & Constraints
Operational Trade-offs
Because embeddings must be generated for every text segment, document indexing is the heaviest operation in the pipeline. However, because this is an intentional one-time upfront cost, subsequent queries and rank fusions complete in a fraction of a second.

Current Bounding Box
AIOS was designed as a local, single-user sandbox to master the foundational mechanics of RAG engineering. To maintain a sharp project scope, the following architecture constraints were intentionally accepted:

State and session histories are maintained in active memory rather than a persistent DB.

File storage and processing are optimized strictly for native text-based PDFs.

Authentication layers are omitted in favor of local-host deployment execution.

 Roadmap & Next Horizons
To take AIOS from a high-performance local pipeline to a production-ready enterprise cluster, future development is focused on:

[ ] Infrastructure Scaling: Migrating session states to Redis caches and scaling document metadata management into a robust PostgreSQL layer.

[ ] Advanced Ingestion: Integrating OCR engines for scanned documents and implementing layout-aware parsers to extract structured tables and inline imagery.

[ ] Streaming Architecture: Refactoring the FastAPI-to-Streamlit pipeline to stream tokens in real-time, lowering the perceived latency of long responses.

[ ] Enterprise Security: Implementing multi-tenant isolation, user authentication, and granular role-based access control.

 Engineering Takeaways
Building AIOS made one thing incredibly clear: the ultimate quality of a RAG system depends far more on data preprocessing and retrieval quality than on the raw power of the LLM itself.

This project provided deep, hands-on experience in balancing precision and recall, optimizing text chunking boundaries, orchestrating multi-service architectures, and handling state across independent backend and frontend services.

 Contributing
Got an idea to optimize the chunking strategy or speed up the fusion ranking? Contributions are welcome.

Fork the project repository.

Cut a clean feature branch (git checkout -b feature/AmazingFeature).

Commit your changes (git commit -m 'Add some AmazingFeature').

Push to the branch (git push origin feature/AmazingFeature).

Open a detailed Pull Request.

 License
Distributed under the MIT License. See LICENSE for more information.

 Author
S.R. Deekshitha

B.Tech in Computer Science Engineering (Artificial Intelligence & Machine Learning)

Interests: Information Retrieval, Retrieval-Augmented Generation (RAG), Natural Language Processing, and Modular Backend Engineering.

GitHub: deekshitha15103-del

 Acknowledgements
AIOS stands on the shoulders of the incredible open-source AI and backend communities. Major thanks to the contributors behind:

FastAPI & Streamlit — For making the Python web ecosystem incredibly productive.

FAISS & Sentence Transformers — For democratic access to elite-tier vector search tooling.

Ollama — For changing the game with local LLM deployment.
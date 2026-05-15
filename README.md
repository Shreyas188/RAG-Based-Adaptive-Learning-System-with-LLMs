# RAG-Based Adaptive Learning System with LLMs

> **AI-powered NCERT Physics tutor** using Retrieval-Augmented Generation (RAG), Sentence Transformers, ChromaDB, and OpenAI GPT.

---

## 🎯 Project Overview

This system answers NCERT Class 12 Physics questions using:
- **Semantic retrieval** of relevant textbook chunks from ChromaDB
- **GPT-3.5/4** for generating accurate, context-grounded answers
- **Adaptive analytics** to track weak topics and personalize learning

### Supported Chapters
| Chapter | Topics |
|---|---|
| Chapter 3: Current Electricity | Ohm's Law, Drift Velocity, Kirchhoff's Laws, EMF, Wheatstone Bridge |
| Chapter 4: Moving Charges and Magnetism | Biot-Savart Law, Ampere's Law, Cyclotron, Galvanometer |

---

## 🏗️ Project Structure

```
RAG/
├── frontend/                    # Streamlit UI
│   ├── app.py                   # Home page + navigation
│   ├── pages/
│   │   ├── 1_Chat.py            # AI chat interface
│   │   ├── 2_Upload.py          # PDF upload page
│   │   ├── 3_Quiz.py            # Interactive quiz
│   │   ├── 4_Summary.py         # Summaries + flashcards
│   │   └── 5_Dashboard.py       # Learning analytics
│   └── assets/style.css         # Dark theme CSS
│
├── backend/                     # FastAPI server
│   ├── main.py                  # App entry point
│   ├── database.py              # SQLite ORM setup
│   ├── api/
│   │   ├── upload.py            # PDF upload endpoints
│   │   ├── chat.py              # Q&A endpoints
│   │   ├── quiz.py              # Quiz endpoints
│   │   ├── summary.py           # Summary + flashcard endpoints
│   │   └── history.py           # Analytics endpoints
│   ├── services/
│   │   ├── pdf_service.py       # PDF extraction
│   │   ├── embedding_service.py # Sentence Transformers
│   │   ├── vector_store_service.py  # ChromaDB operations
│   │   ├── llm_service.py       # OpenAI + HuggingFace
│   │   ├── db_service.py        # SQLite CRUD
│   │   └── adaptive_service.py  # Weak topic detection
│   └── models/schemas.py        # Pydantic schemas
│
├── rag_pipeline/                # RAG orchestration
│   ├── chunker.py               # Semantic text chunking
│   ├── prompt_builder.py        # LLM prompt templates
│   └── pipeline.py              # End-to-end RAG pipeline
│
├── embeddings/
│   └── generate_embeddings.py   # Batch embedding script
│
├── utils/
│   ├── config.py                # Settings (pydantic-settings)
│   ├── logger.py                # Loguru logging
│   ├── text_cleaner.py          # PDF text cleaning
│   └── pdf_exporter.py          # Notes/flashcard PDF export
│
├── data/uploads/                # PDF storage (gitignored)
├── vector_db/chroma_store/      # ChromaDB persistence (gitignored)
├── docs/                        # Documentation
├── notebooks/                   # Jupyter notebooks
├── requirements.txt
├── .env.example
├── Dockerfile.backend
├── Dockerfile.frontend
└── docker-compose.yml
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip
- (Optional) OpenAI API key for GPT responses

### 1. Clone & Setup

```bash
cd "c:\Users\Shrey\OneDrive\Desktop\RAG"

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

> **No OpenAI key?** The system automatically falls back to HuggingFace `flan-t5-base` (free, no key needed, weaker answers).

### 3. Start the Backend (FastAPI)

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API docs will be available at: http://localhost:8000/docs

### 4. Start the Frontend (Streamlit)

```bash
# In a new terminal
streamlit run frontend/app.py
```

Frontend opens at: http://localhost:8501

### 5. Upload NCERT PDFs

1. Download from [ncert.nic.in](https://ncert.nic.in/textbook.php?leph1=0-16):
   - `leph103.pdf` (Current Electricity)
   - `leph104.pdf` (Moving Charges and Magnetism)

2. Go to **Upload PDFs** page in the Streamlit app and upload them.

**OR** use the batch embedding script:
```bash
# Place PDFs in data/uploads/ then run:
python -m embeddings.generate_embeddings
```

### 6. Start Chatting!
Go to the **Chat** page and ask: *"What is Ohm's Law?"*

---

## 🐳 Docker Deployment

### One-command startup

```bash
# Copy and fill your .env file first
copy .env.example .env

# Build and start both services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

| Service | URL |
|---|---|
| Frontend (Streamlit) | http://localhost:8501 |
| Backend (FastAPI) | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

### Stop services

```bash
docker-compose down
```

---

## 🔌 API Reference

All endpoints available at `/docs` (Swagger UI).

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload/` | Upload PDF file |
| `GET` | `/api/upload/documents` | List uploaded documents |
| `GET` | `/api/upload/chapters` | Get available chapters |
| `POST` | `/api/chat/` | Ask a question (RAG) |
| `GET` | `/api/chat/history/{session_id}` | Get chat history |
| `DELETE` | `/api/chat/history/{session_id}` | Clear history |
| `POST` | `/api/quiz/generate` | Generate MCQ quiz |
| `POST` | `/api/quiz/submit` | Submit + score quiz |
| `POST` | `/api/summary/` | Generate chapter summary |
| `POST` | `/api/summary/flashcards` | Generate flashcards |
| `POST` | `/api/summary/export-notes` | Export notes as PDF |
| `GET` | `/api/analytics/{session_id}` | Get learning analytics |
| `GET` | `/api/analytics/weak-topics/{session_id}` | Get weak topic analysis |
| `GET` | `/health` | System health check |

---

## 🧠 RAG Pipeline Architecture

```
User Query
    │
    ▼
Query Embedding (all-MiniLM-L6-v2)
    │
    ▼
ChromaDB Similarity Search (Top-K chunks)
    │
    ▼
Context Validation (relevance threshold)
    │
    ▼
Prompt Construction (system + context + query)
    │
    ▼
LLM Generation (OpenAI GPT / HuggingFace)
    │
    ▼
Response + Source References
```

---

## ⚙️ Configuration Options

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | GPT model name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer |
| `CHUNK_SIZE` | `500` | Max chars per chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `TOP_K_RESULTS` | `5` | Chunks retrieved per query |
| `USE_OPENAI` | `true` | Use OpenAI vs HuggingFace |
| `HF_MODEL_NAME` | `google/flan-t5-base` | Fallback LLM model |

---

## 🧪 Running Tests

```bash
pytest backend/tests/ -v
```

---

## 📚 Features

| Feature | Status |
|---|---|
| PDF Upload & Processing | ✅ |
| Semantic Text Chunking | ✅ |
| Vector Embeddings (MiniLM) | ✅ |
| ChromaDB Vector Store | ✅ |
| RAG Q&A Pipeline | ✅ |
| OpenAI GPT Integration | ✅ |
| HuggingFace Fallback | ✅ |
| Chapter-wise Filtering | ✅ |
| Source Citations | ✅ |
| MCQ Quiz Generation | ✅ |
| Quiz Scoring & Feedback | ✅ |
| Chapter Summaries | ✅ |
| Flashcard Generation | ✅ |
| PDF Export (Notes/Flashcards) | ✅ |
| Chat History (SQLite) | ✅ |
| Learning Analytics Dashboard | ✅ |
| Weak Topic Detection | ✅ |
| Adaptive Study Plan | ✅ |
| Docker Support | ✅ |
| Dark Theme UI | ✅ |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit 1.35 |
| Backend | FastAPI 0.111 + Uvicorn |
| PDF Parsing | pdfplumber + PyPDF2 |
| Text Chunking | LangChain RecursiveCharacterTextSplitter |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 |
| Vector Database | ChromaDB (persistent) |
| LLM (primary) | OpenAI GPT-3.5-turbo |
| LLM (fallback) | HuggingFace flan-t5-base |
| Database | SQLite + SQLAlchemy (async) |
| Logging | Loguru |
| PDF Export | fpdf2 |
| Charts | Plotly |
| Containerization | Docker + docker-compose |

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgments

- [NCERT](https://ncert.nic.in/) for free educational content
- [LangChain](https://langchain.com/) for RAG framework
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Sentence Transformers](https://sbert.net/) for embeddings
- [OpenAI](https://openai.com/) for GPT API

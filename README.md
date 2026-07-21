# ✈️ Multi-modal Airline Customer Support Chatbot

An AI-powered airline customer support assistant built using a **FastAPI** backend and a **React (Vite)** frontend. The system uses **Retrieval-Augmented Generation (RAG)** with **ChromaDB** and **SentenceTransformers** to answer airline policy, baggage rules, cancellation policies, and FAQ questions with high accuracy and low latency. It also supports multimodal inputs, including PDF text extraction and image verification.

---

## 🌟 Key Features

1. **Retrieval-Augmented Generation (RAG) Engine**:
   * Semantic vector search using `SentenceTransformer("all-MiniLM-L6-v2")` embeddings.
   * Persistent vector database using **ChromaDB**.
   * Dynamic prompt construction with strict system guardrails to prevent hallucination.
2. **Lifespan Model Caching**:
   * Pre-loads embedding models, vector store collections, and LLM clients during FastAPI startup inside `app.state`.
   * Eliminates runtime cold-start latencies for instant query responses.
3. **Multimodal Document & File Processing**:
   * **PDF Processor**: Extracts raw text from uploaded PDF documents using PyMuPDF (`fitz`) and injects it into prompt context.
   * **Image Processor**: Validates uploaded images (formats: `.jpg`, `.jpeg`, `.png`, `.webp`) for document verification.
   * **Input Router**: Automatically detects file types (`.pdf`, `.png`/`.jpg`, or query string) and routes to specialized handlers.
4. **Interactive Dark-Mode Chatbot UI**:
   * Staged file badges for quick attachments.
   * Auto-scroll feed, quick-action prompts, and source citations with distance scores.

---

## 🏗️ Architecture & Pipeline Walkthrough

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           REACT FRONTEND (Vite)                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP POST Requests
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                               │
│                                                                         │
│  ┌───────────────────┐    ┌───────────────────┐   ┌──────────────────┐  │
│  │   POST /chat      │    │ POST /upload/pdf  │   │POST /upload/image│  │
│  └─────────┬─────────┘    └─────────┬─────────┘   └────────┬─────────┘  │
│            │                        │                      │            │
│            ▼                        ▼                      ▼            │
│    ┌──────────────┐         ┌──────────────┐       ┌──────────────┐     │
│    │ RAG Retriever│         │ PDFProcessor │       │ImageProcessor│     │
│    └───────┬──────┘         └───────┬──────┘       └───────┬──────┘     │
│            │ (Similarity)           │ (Extracted           │ (Status)   │
│            ▼                        ▼ Text)                ▼            │
│    ┌──────────────┐         ┌──────────────┐       ┌──────────────┐     │
│    │  ChromaDB    │         │Context Inject│       │ Client Resp  │     │
│    └───────┬──────┘         └───────┬──────┘       └──────────────┘     │
│            │                        │                                   │
│            └───────────┬────────────┘                                   │
│                        ▼                                                │
│              ┌──────────────────┐                                       │
│              │  Prompt Builder  │                                       │
│              └─────────┬────────┘                                       │
│                        │ (System Role + Context + User Query)           │
│                        ▼                                                │
│              ┌──────────────────┐                                       │
│              │   Groq LLM API   │                                       │
│              └─────────┬────────┘                                       │
│                        │                                                │
└────────────────────────┼────────────────────────────────────────────────┘
                         │ Structured JSON Answer + Sources
                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             USER INTERFACE                              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Detailed Pipeline Stages

#### Stage 1: Knowledge Base Ingestion & Vector Indexing
1. **Document Loading**: `load_documents()` in `app/rag/document_loader.py` reads Markdown policy files (`baggage_policy.md`, `cancellation_policy.md`, `faq.md`, etc.) from `backend/knowledge_base/`.
2. **Text Chunking**: `split_documents()` in `app/rag/text_chunker.py` breaks long policy files into optimized chunks using `RecursiveCharacterTextSplitter`.
3. **Embedding Generation**: `generate_document_embeddings()` in `app/rag/embedding_generator.py` embeds each text chunk into 384-dimensional dense vectors using `SentenceTransformer("all-MiniLM-L6-v2")`.
4. **Vector Storage**: `create_vector_store()` in `app/rag/vector_store.py` persists the chunks and vector embeddings into a local **ChromaDB** collection (`airline_knowledge_base`).

#### Stage 2: Multimodal Input Detection & Routing
* `InputRouter` in `app/multimodal/input_router.py` inspects file extension types:
  * `.pdf` $\rightarrow$ `PDFProcessor.extract_text()` via PyMuPDF (`fitz`).
  * `.jpg`, `.jpeg`, `.png`, `.webp` $\rightarrow$ `ImageProcessor.process_image()`.
  * Plain Query $\rightarrow$ Standard RAG Query Flow.

#### Stage 3: Retrieval & Context Assembly
1. The user query is converted into a vector embedding using the cached SentenceTransformer model.
2. `retrieve_documents()` queries ChromaDB to return the top `k=3` most relevant policy chunks based on cosine distance.
3. `build_prompt()` constructs a strict system prompt containing:
   * Guardrail instructions (never fabricate policies; state "I couldn't find that information..." if ungrounded).
   * Retrieved document context blocks.
   * User query.

#### Stage 4: LLM Answer Synthesis & Citation Formatting
1. `LLMClient` sends the constructed prompt to Groq (`llama-3.3-70b-versatile` or configured LLM).
2. The response is packaged into a `ChatResponse` model including answer text, source metadata, and match distance metrics.

---

## 📁 Project Folder Structure

```text
airline-rag-chatbot/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── models/            # Pydantic schemas (ChatRequest, ChatResponse, UploadResponse)
│   │   │   │   ├── chat_models.py
│   │   │   │   ├── response_models.py
│   │   │   │   └── __init__.py
│   │   │   └── routes/            # FastAPI Endpoint Routers
│   │   │       ├── chat.py        # POST /chat endpoint for RAG queries
│   │   │       ├── health.py      # GET /health endpoint for diagnostics
│   │   │       ├── upload.py      # POST /upload/pdf & POST /upload/image
│   │   │       └── __init__.py
│   │   │
│   │   ├── multimodal/            # PDF and Image Processors & Router
│   │   │   ├── image_processor.py
│   │   │   ├── input_router.py
│   │   │   ├── pdf_processor.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── rag/                   # RAG Core Pipeline Modules
│   │   │   ├── document_loader.py
│   │   │   ├── embedding_generator.py
│   │   │   ├── llm_client.py
│   │   │   ├── prompt_builder.py
│   │   │   ├── retriever.py
│   │   │   ├── text_chunker.py
│   │   │   └── vector_store.py
│   │   │
│   │   ├── services/              # Domain Services (Flight, Booking, Baggage, Weather, Airport)
│   │   └── main.py                # FastAPI Application & Lifespan Setup
│   │
│   ├── chroma_db/                 # Persistent ChromaDB storage directory
│   ├── knowledge_base/            # Markdown policy documents source
│   ├── scratch/
│   │   └── test_backend.py        # Automated diagnostic endpoint test script
│   ├── test_pipeline.py           # CLI Interactive Pipeline Test Script
│   ├── requirements.txt           # Python dependency specifications
│   └── .env                       # Backend Environment Variables (GROQ_API_KEY)
│
└── frontend/
    ├── src/
    │   ├── services/
    │   │   └── api.js             # Axios API client functions
    │   ├── App.jsx                # Main Chatbot UI Component
    │   ├── App.css                # Dark mode styles & animations
    │   ├── index.css              # Typography & reset styles
    │   └── main.jsx               # React entry point
    ├── package.json               # Node.js dependencies
    └── vite.config.js             # Vite development server configuration
```

---

## 📋 Prerequisites

Ensure your system meets the following requirements before setup:

| Dependency | Minimum Version | Notes |
| :--- | :--- | :--- |
| **Python** | 3.10+ | Required for FastAPI backend & ML dependencies |
| **Node.js** | 18+ (LTS) | Required for Vite + React frontend |
| **npm** | 9+ | Comes bundled with Node.js |
| **Groq API Key** | Free tier available | Obtain from [Groq Console](https://console.groq.com/) |

---

## 🛠️ Step-by-Step Installation & Setup Guide

### Step 1: Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

---

### Step 2: Backend Setup

Open a terminal and navigate to the `backend/` directory:

```powershell
cd backend
```

1. **Create Virtual Environment**:
   * **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     ```
   * **Linux / macOS**:
     ```bash
     python3 -m venv venv
     ```

2. **Activate Virtual Environment**:
   * **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\activate
     ```
   * **Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

### Step 3: Frontend Setup

Open a second terminal window and navigate to the `frontend/` directory:

```powershell
cd frontend
```

1. **Install Node Dependencies**:
   ```bash
   npm install
   ```

---

## 🚀 Running the Application

### 1. Launch FastAPI Backend

From the `backend/` directory (with virtual environment activated):

```powershell
uvicorn app.main:app --port 8000 --reload
```

* Backend server will run at: `http://localhost:8000`
* Interactive API Docs (Swagger UI): `http://localhost:8000/docs`
* Alternative Docs (ReDoc): `http://localhost:8000/redoc`
* Health Check Endpoint: `http://localhost:8000/health`

### 2. Launch React Frontend

From the `frontend/` directory:

```powershell
npm run dev
```

* Frontend dev server will run at: `http://localhost:5173`
* Open your browser and visit `http://localhost:5173` to interact with the chatbot!

---

## 🧪 Testing & Diagnostics

### Run Automated Backend Diagnostic Tests
To verify API lifespan initialization, endpoint responses, RAG search, and file upload endpoints:

From the `backend/` directory:
```powershell
python scratch/test_backend.py
```
*Expected Output*: `ALL API ENDPOINT DIAGNOSTIC TESTS PASSED!`

### Run Interactive CLI Pipeline Test
To test the pipeline step-by-step in the terminal (text, PDF, or image input):

From the `backend/` directory:
```powershell
python test_pipeline.py
```

---

## 🔌 API Endpoint Reference

| Method | Endpoint | Description | Request Body / Payload |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Server health and component status | None |
| `POST` | `/chat` | Submit question for RAG answer generation | `{"message": "What is the baggage allowance?"}` |
| `POST` | `/upload/pdf` | Upload PDF file for text extraction | `multipart/form-data` (`file`) |
| `POST` | `/upload/image`| Upload Image file for document validation | `multipart/form-data` (`file`) |

---

## ❓ Troubleshooting

* **Missing Groq API Key Error**:
  * Ensure `GROQ_API_KEY` is present in `backend/.env`.
  * Ensure the `.env` file is placed directly inside `backend/` (not root).
* **ChromaDB SQLite / Dependency Error**:
  * Verify Python version is 3.10 or higher.
* **CORS / Network Error in UI**:
  * Verify backend is running on `http://localhost:8000` before sending messages from the React app.
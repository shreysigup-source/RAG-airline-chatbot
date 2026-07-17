import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

import chromadb
from app.rag.embedding_generator import load_embedding_model
from app.rag.llm_client import LLMClient
from app.api.routes import chat_router, upload_router, health_router

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous lifespan manager that pre-loads models and initialises 
    ChromaDB connections on startup, cleaning up resources on shutdown.
    """
    logger.info("Initializing system resources on startup...")
    try:
        # Load embedding model
        app.state.embedding_model = load_embedding_model()
        logger.info("SentenceTransformer embedding model loaded successfully.")

        # Connect to ChromaDB
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # chroma_db is placed under backend/chroma_db, which is parallel to backend/app/
        db_path = os.path.abspath(os.path.join(base_dir, "..", "chroma_db"))
        logger.info(f"Connecting to ChromaDB collection at path: '{db_path}'")
        
        db_client = chromadb.PersistentClient(path=db_path)
        app.state.chroma_collection = db_client.get_or_create_collection(
            name="airline_knowledge_base"
        )
        logger.info("ChromaDB collection loaded successfully.")

        # Load Groq Client
        app.state.llm_client = LLMClient()
        logger.info("Groq LLM Client initialized successfully.")

    except Exception as e:
        logger.error(f"Startup initialization failed: {str(e)}", exc_info=True)
        # Prevent API crashes but flags degraded state
        app.state.embedding_model = None
        app.state.chroma_collection = None
        app.state.llm_client = None

    yield
    logger.info("Cleaning up system resources on shutdown...")

# Instantiate FastAPI application
app = FastAPI(
    title="Airline RAG Chatbot API",
    description="Full-featured backend exposing RAG and function calling routes for airline customer service.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow React dev server or any web client
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers with clear tags
app.include_router(health_router, prefix="/health", tags=["Health Checks"])
app.include_router(upload_router, prefix="/upload", tags=["Multimodal Uploads"])
app.include_router(chat_router, prefix="/chat", tags=["Conversation Chat"])

@app.get("/", tags=["General"])
async def read_root():
    """
    Welcome landing page pointing to the documentation endpoints.
    """
    return {
        "status": "success",
        "message": "Welcome to the Airline RAG Chatbot API.",
        "documentation": "/docs"
    }

# ----------------- GLOBAL EXCEPTION HANDLERS -----------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Format validation details nicely
    details = []
    for err in errors:
        location = " -> ".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Value is invalid")
        details.append(f"{location}: {msg}")
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": f"Validation failed: {', '.join(details)}"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"An unhandled internal server error occurred: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": f"An internal server error occurred: {str(exc)}"
        }
    )

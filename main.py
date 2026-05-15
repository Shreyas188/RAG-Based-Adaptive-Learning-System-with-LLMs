"""
backend/main.py
----------------
FastAPI application entry point.
Registers all routers, configures CORS, middleware, startup events, and health checks.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from backend.database import init_db
from backend.api import upload, chat, quiz, summary, history
from backend.services.vector_store_service import get_vector_store
from backend.services.llm_service import get_llm_service
from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


# ============================================================
# Application Lifespan (startup / shutdown)
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    - Startup: Initialize DB, warm up services
    - Shutdown: Clean up resources
    """
    logger.info("=" * 60)
    logger.info("🚀 RAG Adaptive Learning System starting up...")
    logger.info("=" * 60)

    # Initialize SQLite database tables
    await init_db()
    logger.info("✅ Database initialized")

    # Warm up vector store (connects to ChromaDB)
    try:
        vs = get_vector_store()
        stats = vs.get_collection_stats()
        logger.info(f"✅ Vector store ready: {stats['total_chunks']} chunks, chapters: {stats['chapters']}")
    except Exception as e:
        logger.warning(f"⚠️ Vector store init warning: {e}")

    # Pre-load LLM service
    try:
        llm = get_llm_service()
        info = llm.get_backend_info()
        logger.info(f"✅ LLM service ready: {info}")
    except Exception as e:
        logger.warning(f"⚠️ LLM service warning: {e}")

    logger.info("🎓 RAG Adaptive Learning System is ready!")
    logger.info(f"📖 API docs available at: http://{settings.backend_host}:{settings.backend_port}/docs")

    yield  # Application runs here

    logger.info("🛑 RAG Adaptive Learning System shutting down...")


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="RAG-Based Adaptive Learning System",
    description=(
        "An AI-powered adaptive learning assistant using NCERT Physics textbooks. "
        "Features RAG-based Q&A, quiz generation, chapter summaries, and adaptive analytics."
    ),
    version="1.0.0",
    contact={
        "name": "RAG Learning System",
        "url": "https://github.com/your-repo/rag-adaptive-learning",
    },
    license_info={"name": "MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ============================================================
# Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Routers
# ============================================================

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(quiz.router)
app.include_router(summary.router)
app.include_router(history.router)


# ============================================================
# Health & Root Endpoints
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — returns API info."""
    return {
        "name": "RAG-Based Adaptive Learning System",
        "version": "1.0.0",
        "description": "AI-powered NCERT Physics learning assistant",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for Docker and load balancers.

    Returns:
        System status and component health indicators.
    """
    try:
        vs = get_vector_store()
        stats = vs.get_collection_stats()
        llm = get_llm_service()
        llm_info = llm.get_backend_info()

        return {
            "status": "healthy",
            "vector_store_docs": stats["total_chunks"],
            "available_chapters": stats["chapters"],
            "llm_backend": llm_info["backend"],
            "llm_model": llm_info["model"],
            "embedding_model": settings.embedding_model,
            "version": "1.0.0",
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
            },
        )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
        workers=1 if settings.debug else 2,
        log_level=settings.log_level.lower(),
    )

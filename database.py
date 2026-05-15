"""
backend/database.py
--------------------
SQLite database setup using SQLAlchemy + aiosqlite.
Creates all tables and provides async session management.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean,
    create_engine, event,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
import json

from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


# ============================================================
# Database Base & Engine
# ============================================================

class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


def get_db_url() -> str:
    """Get async SQLite database URL."""
    db_path = settings.get_db_path()
    return f"sqlite+aiosqlite:///{db_path}"


# Async engine for FastAPI
async_engine = create_async_engine(
    get_db_url(),
    echo=False,  # Set True to log SQL queries
    connect_args={"check_same_thread": False},
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ============================================================
# ORM Models
# ============================================================

class UploadedDocument(Base):
    """Stores metadata for uploaded PDF documents."""
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    chapter_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    file_path = Column(String(512), nullable=False)
    total_pages = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    total_words = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    upload_timestamp = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)


class ChatHistory(Base):
    """Stores all chat messages per session."""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(128), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True)  # JSON string of source references
    confidence = Column(Float, nullable=True)
    chapter_filter = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=func.now())


class QuizAttempt(Base):
    """Stores quiz attempt results."""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(128), index=True, nullable=False)
    chapter_name = Column(String(255), nullable=False)
    difficulty = Column(String(20), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    feedback_json = Column(Text, nullable=True)  # JSON feedback
    timestamp = Column(DateTime, default=func.now())


class UserProgress(Base):
    """Tracks user learning progress per chapter."""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(128), index=True, nullable=False)
    chapter_name = Column(String(255), nullable=False)
    query_count = Column(Integer, default=0)
    last_activity = Column(DateTime, default=func.now())
    avg_quiz_score = Column(Float, default=0.0)
    quiz_attempts = Column(Integer, default=0)


class QueryLog(Base):
    """Logs individual queries for analytics."""
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(128), index=True)
    query_text = Column(Text, nullable=False)
    chapter_filter = Column(String(255), nullable=True)
    response_confidence = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=func.now())


# ============================================================
# Database Initialization
# ============================================================

async def init_db() -> None:
    """Create all database tables if they don't exist."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully.")


async def get_db_session() -> AsyncSession:
    """
    Async context manager for database sessions.
    Used as FastAPI dependency injection.

    Yields:
        AsyncSession object.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

"""
Database connection and session management
- Requires DATABASE_URL (Supabase Postgres) to be provided
"""

import os
import logging
from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import SQLAlchemy Base models
try:
	from models.database import Base
except Exception:
	Base = None  # type: ignore


def _ensure_ssl_in_postgres_url(database_url: str) -> str:
	"""Ensure ?sslmode=require is present for Postgres URLs (e.g., Supabase)."""
	parsed = urlparse(database_url)
	if parsed.scheme.startswith("postgres"):
		query = parsed.query
		if "sslmode=" not in query:
			query = f"{query}&sslmode=require" if query else "sslmode=require"
		return urlunparse(parsed._replace(query=query))
	return database_url


# Initialize database variables
RAW_DATABASE_URL = os.getenv("DATABASE_URL")

# Use the DATABASE_URL from .env file (which should point to Supabase Session Pooler)
if RAW_DATABASE_URL:
    logger.info(f"Using DATABASE_URL from environment: {RAW_DATABASE_URL.split('@')[1] if '@' in RAW_DATABASE_URL else '***'}")
else:
    logger.warning("DATABASE_URL is not set - database operations will be disabled")

if not RAW_DATABASE_URL:
    logger.warning("DATABASE_URL is not set - database operations will be disabled")
    # Create dummy engines that will fail gracefully
    engine = None
    async_engine = None
    SessionLocal = None
    AsyncSessionLocal = None
else:
    DATABASE_URL = _ensure_ssl_in_postgres_url(RAW_DATABASE_URL)

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
    )

    # Create async engine for async operations
    # asyncpg doesn't use sslmode in the URL, it handles SSL differently
    async_database_url = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://").replace("postgresql://", "postgresql+asyncpg://")

    # Remove sslmode from async URL as asyncpg handles it differently
    if "sslmode=" in async_database_url:
        # Parse and reconstruct URL without sslmode
        parsed = urlparse(async_database_url)
        query_parts = parsed.query.split("&")
        query_parts = [part for part in query_parts if not part.startswith("sslmode=")]
        new_query = "&".join(query_parts) if query_parts else ""
        async_database_url = urlunparse(parsed._replace(query=new_query))

    async_engine = create_async_engine(
        async_database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        poolclass=None,  # Disable connection pooling entirely
        connect_args={"statement_cache_size": 0}  # Disable statement cache for pgbouncer compatibility
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    AsyncSessionLocal = sessionmaker(
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        bind=async_engine
    )


def create_tables() -> None:
    """Create all database tables if Base is available."""
    if Base is None or engine is None:
        logger.warning("Cannot create tables - Base or engine not available")
        return
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning(f"Table creation failed: {e}")
        # Table creation failures should not crash startup; handled via migrations in prod


def get_db() -> Session:
    """Provide a database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not configured - DATABASE_URL is required")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """Provide an async database session."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not configured - DATABASE_URL is required")
    async with AsyncSessionLocal() as session:
        yield session


def init_database() -> None:
    """Initialize database (no-op if using migrations)."""
    if engine is not None:
        create_tables()
    else:
        logger.warning("Database initialization skipped - no engine available")

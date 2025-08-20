"""
Database connection and session management
- Requires DATABASE_URL (Supabase Postgres) to be provided
"""

import os
from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

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


RAW_DATABASE_URL = os.getenv("DATABASE_URL")
if not RAW_DATABASE_URL:
	raise RuntimeError("DATABASE_URL is required and must point to your Supabase Postgres instance")

DATABASE_URL = _ensure_ssl_in_postgres_url(RAW_DATABASE_URL)

engine = create_engine(
	DATABASE_URL,
	pool_pre_ping=True,
	pool_recycle=300,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
	"""Create all database tables if Base is available."""
	if Base is None:
		return
	try:
		Base.metadata.create_all(bind=engine)
	except Exception:
		# Table creation failures should not crash startup; handled via migrations in prod
		pass


def get_db() -> Session:
	"""Provide a database session."""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def init_database() -> None:
	"""Initialize database (no-op if using migrations)."""
	create_tables()

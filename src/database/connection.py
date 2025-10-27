"""Database connection management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .models import Base

# Database URL from environment variable or default to SQLite for local development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ml_registry.db"  # Local SQLite for development
)

# For PostgreSQL (production/AWS RDS), format should be:
# postgresql://username:password@host:port/database
# Example: postgresql://admin:password@db.example.com:5432/ml_registry

# Create engine
# For SQLite, we need check_same_thread=False for FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=bool(os.getenv("SQL_ECHO", "False").lower() == "true"),  # Log SQL queries if SQL_ECHO=true
    pool_pre_ping=True,  # Verify connections before using them
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db() -> None:
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.
    
    Usage in FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
            pass
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db() -> None:
    """
    Reset database by dropping and recreating all tables.
    
    WARNING: This will delete all data!
    Use only for testing or the /reset endpoint.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

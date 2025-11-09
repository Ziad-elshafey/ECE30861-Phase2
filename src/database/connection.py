"""Database connection management."""

import os
import re
from sqlalchemy import create_engine, event
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


# Register REGEXP function for SQLite
@event.listens_for(engine, "connect")
def enable_sqlite_regexp(dbapi_connection, connection_record):
    """
    Enable REGEXP operator for SQLite.
    
    SQLite doesn't have built-in regex support, so we need to provide
    a custom function using Python's re module.
    """
    if DATABASE_URL.startswith("sqlite"):
        def regexp(pattern, value):
            """Regex matching function for SQLite."""
            if value is None or pattern is None:
                return False
            try:
                return re.search(pattern, value, re.IGNORECASE) is not None
            except re.error:
                return False
        
        dbapi_connection.create_function("regexp", 2, regexp)


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

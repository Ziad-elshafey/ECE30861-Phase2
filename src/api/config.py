"""Configuration settings for the FastAPI application."""

import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ml_registry.db")
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "600"))
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "ML Model Registry"
    PROJECT_VERSION: str = "1.0.0"
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # TODO: Restrict in production
    
    # AWS (for future use)
    AWS_REGION: Optional[str] = os.getenv("AWS_REGION")
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET")
    
    # Default admin user (as per spec)
    DEFAULT_ADMIN_USERNAME: str = "ece30861defaultadminuser"
    DEFAULT_ADMIN_PASSWORD: str = '''correcthorsebatterystaple123(!__+@**(A'"`;DROP TABLE packages;'''
    DEFAULT_ADMIN_EMAIL: str = "admin@mlregistry.local"


settings = Settings()

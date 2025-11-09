"""Main FastAPI application factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.config import settings
from src.api.routes import users, packages, ratings, system
from src.database.connection import init_db, reset_db
from src.database.init_db import create_default_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup: Initialize database and create default user
    print("🚀 Starting ML Registry API...")
    init_db()
    create_default_user()
    print("✅ Database initialized with default admin user")
    yield
    # Shutdown: Clean up resources if needed
    print("🛑 Shutting down ML Registry API...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="A Trustworthy Model Registry for Machine Learning Models",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(
        users.router,
        prefix=f"{settings.API_V1_PREFIX}/user",
        tags=["users"]
    )
    
    app.include_router(
        packages.router,
        prefix=f"{settings.API_V1_PREFIX}/package",
        tags=["packages"]
    )
    
    app.include_router(
        ratings.router,
        prefix=f"{settings.API_V1_PREFIX}/package",
        tags=["ratings"]
    )
    
    app.include_router(
        system.router,
        prefix=f"{settings.API_V1_PREFIX}/system",
        tags=["system"]
    )
    
    # Root endpoint
    @app.get("/", tags=["root"])
    def root():
        """Root endpoint with API information."""
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "docs": "/docs",
            "health": "/health"
        }
    
    # Health endpoint for autograder/monitoring (public, no auth required)
    @app.get("/health", tags=["health"])
    def health_check():
        """
        Simple health check endpoint for monitoring and autograder.
        Always returns 200 OK with status 'ok'.
        This is a public endpoint with no authentication required.
        """
        return {"status": "ok"}
    
    # Tracks endpoint for autograder (public, no auth required)
    @app.get("/tracks", tags=["tracks"])
    def get_tracks():
        """
        Return available feature tracks implemented in the system.
        This endpoint is used by the autograder to verify implemented features.
        
        Implemented Tracks:
        - Access Control: Complete user authentication and authorization system
          * User registration and login with JWT tokens
          * Role-based permissions (admin, upload, download, search)
          * Secure password hashing with bcrypt
          * Token-based authentication for API endpoints
          * User account management (create, read, update, delete)
        
        Returns:
            List of track names as strings
        """
        return {
            "plannedTracks": ["Access Control"],
            "tracks": [
                {
                    "name": "Access Control",
                    "description": "User authentication, authorization, and permission management",
                    "features": [
                        "User registration and authentication",
                        "JWT token-based authorization",
                        "Role-based access control (RBAC)",
                        "Admin and regular user roles",
                        "Secure password storage with bcrypt",
                        "Token expiration and refresh",
                        "User permission management"
                    ],
                    "endpoints": [
                        "POST /api/v1/user/register",
                        "POST /api/v1/user/login",
                        "GET /api/v1/user/me",
                        "DELETE /api/v1/user/{username}"
                    ]
                }
            ]
        }
    
    # Reset endpoint for autograder (public, no auth required)
    @app.delete("/reset", tags=["system"])
    def reset_system():
        """
        Reset the system to default state (empty registry with default user).
        This endpoint is used by the autograder to reset the system between tests.
        
        WARNING: This deletes all data including packages, scores, and users
        except for the default admin user which is recreated.
        
        Returns:
            Success message confirming system reset
        """
        try:
            # Reset database (drops all tables and recreates them)
            reset_db()
            
            # Recreate the default admin user
            create_default_user()
            
            return {
                "message": "System reset successful",
                "status": "ok"
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "message": f"System reset failed: {str(e)}",
                    "status": "error"
                }
            )
    
    return app


# Create the app instance for uvicorn
app = create_app()

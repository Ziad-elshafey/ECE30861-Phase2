"""Main FastAPI application factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from src.api.config import settings
from src.api.routes import users, packages, ratings, system
from src.database.connection import init_db, reset_db
from src.database.init_db import create_default_user
from src.api.dependencies import get_db, get_optional_user
from src.database.models import Package
from src.database import crud


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
            # Clean up physical storage artifacts
            import shutil
            from pathlib import Path
            storage_path = Path("storage/artifacts")
            if storage_path.exists():
                # Remove all model files but keep the directory structure
                models_path = storage_path / "models"
                if models_path.exists():
                    shutil.rmtree(models_path)
                    models_path.mkdir(parents=True, exist_ok=True)
                
                # Reset metadata file
                metadata_file = storage_path / "metadata.json"
                if metadata_file.exists():
                    metadata_file.write_text("{}")
            
            # Reset database (drops all tables and recreates them)
            reset_db()
            
            # Recreate the default admin user
            create_default_user()
            
            return {
                "message": "Registry is reset",
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "message": f"System reset failed: {str(e)}",
                }
            )
    
    # Artifacts query endpoint (OpenAPI spec)
    # Schemas
    class ArtifactQuery(BaseModel):
        """Query for artifacts."""
        name: str
        types: Optional[list[str]] = None

    class ArtifactMetadata(BaseModel):
        """Artifact metadata response."""
        name: str
        id: str
        type: str

    @app.post(
        "/artifacts",
        response_model=list[ArtifactMetadata],
        tags=["artifacts"]
    )
    def query_artifacts(
        queries: list[ArtifactQuery],
        offset: Optional[str] = Query(None),
        db: Session = Depends(get_db),
    ):
        """
        Query artifacts from the registry.
        Use name="*" to list all artifacts.
        
        Args:
            queries: List of artifact queries
            offset: Pagination offset
            db: Database session
            
        Returns:
            List of matching artifact metadata
        """
        results = []
        
        for query in queries:
            if query.name == "*":
                # List all artifacts
                packages = crud.get_packages(db, skip=0, limit=1000)
                for pkg in packages:
                    artifact_type = getattr(pkg, 'artifact_type', 'model')
                    results.append(
                        ArtifactMetadata(
                            name=pkg.name,
                            id=str(pkg.id),
                            type=artifact_type
                        )
                    )
            else:
                # Search by name
                packages = db.query(Package).filter(
                    Package.name.like(f"%{query.name}%")
                ).all()
                
                for pkg in packages:
                    artifact_type = getattr(pkg, 'artifact_type', 'model')
                    if query.types and artifact_type not in query.types:
                        continue
                        
                    results.append(
                        ArtifactMetadata(
                            name=pkg.name,
                            id=str(pkg.id),
                            type=artifact_type
                        )
                    )
        
        return results
    
    # Ingest artifact endpoint (OpenAPI spec)
    class ArtifactData(BaseModel):
        """Artifact data for ingest."""
        url: str

    class ArtifactIngestResponse(BaseModel):
        """Response from artifact ingest."""
        metadata: ArtifactMetadata
        data: ArtifactData

    @app.post(
        "/artifact/{artifact_type}",
        response_model=ArtifactIngestResponse,
        status_code=201,
        tags=["artifacts"]
    )
    async def ingest_artifact(
        artifact_type: str,
        artifact_data: ArtifactData,
        db: Session = Depends(get_db),
    ):
        """
        Ingest a new artifact from a URL.
        
        Args:
            artifact_type: Type of artifact (model, dataset, code)
            artifact_data: URL to artifact
            db: Database session
            
        Returns:
            Created artifact metadata and data
        """
        from src.ingest import validate_and_ingest
        import uuid
        
        # Parse model name from URL
        url = artifact_data.url
        model_name = url.strip("/").split("/")[-2:]
        model_name = "/".join(model_name) if len(model_name) == 2 else model_name[0]  # noqa: E501
        
        # Validate model against quality gate
        passes_gate, validation_result = await validate_and_ingest(
            model_name
        )
        
        if not passes_gate:
            # Quality gate failed - return 424
            from fastapi import HTTPException
            raise HTTPException(
                status_code=424,
                detail={
                    "message": "Artifact disqualified due to ratings",
                    "failing_metrics": validation_result.get("failing_metrics")  # noqa: E501
                }
            )
        
        # Quality gate passed - create artifact entry
        artifact_id = str(uuid.uuid4())
        
        # Store in database
        from src.database import crud
        package = crud.create_package(
            db,
            name=model_name,
            version="1.0.0",
            s3_key=artifact_id,
            uploaded_by=1  # Default admin user
        )
        
        # Return response
        return ArtifactIngestResponse(
            metadata=ArtifactMetadata(
                name=model_name,
                id=str(package.id),
                type=artifact_type
            ),
            data=ArtifactData(url=url)
        )
    
    return app


# Create the app instance for uvicorn
app = create_app()

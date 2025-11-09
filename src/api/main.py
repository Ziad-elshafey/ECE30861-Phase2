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
            artifact_type=artifact_type,  # Pass the artifact type
            s3_key=artifact_id,
            s3_bucket="",  # Local storage, no S3
            file_size_bytes=0,  # Will be updated later
            source_url=url,
            uploaded_by=1  # Default admin user
        )
        
        # Store the quality gate scores in database
        if validation_result and validation_result.get("all_scores"):
            scores = validation_result["all_scores"]
            crud.create_or_update_package_score(
                db,
                package_id=package.id,
                ramp_up_time=scores.get("ramp_up_time", 0.0),
                bus_factor=scores.get("bus_factor", 0.0),
                performance_claims=scores.get("performance_claims", 0.0),
                license_score=scores.get("license_score", 0.0),
                dataset_quality=scores.get("dataset_quality", 0.0),
                dataset_code_linkage=scores.get("dataset_and_code", 0.0),
                code_quality=scores.get("code_quality", 0.0),
                reproducibility=scores.get("reproducibility", 0.0),
                reviewedness=scores.get("reviewedness", 0.0),
                net_score=scores.get("net_score", 0.0)
            )
        
        # Return response (per OpenAPI spec - no scores in ingest response)
        return ArtifactIngestResponse(
            metadata=ArtifactMetadata(
                name=model_name,
                id=str(package.id),
                type=artifact_type
            ),
            data=ArtifactData(url=url)
        )
    
    # Rate endpoint - GET /artifact/model/{id}/rate (BASELINE)
    @app.get(
        "/artifact/model/{id}/rate",
        tags=["artifacts"],
        status_code=200
    )
    def get_model_rating(
        id: str,
        db: Session = Depends(get_db),
    ):
        """
        Get ratings/scores for a model artifact.
        
        Per OpenAPI spec: Returns ModelRating with all quality metrics.
        This is separate from the ingest endpoint.
        
        Args:
            id: Artifact ID
            db: Database session
            
        Returns:
            ModelRating with all scores
        """
        from fastapi import HTTPException
        
        # Get package by ID
        try:
            package_id = int(id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid artifact ID format"
            )
        
        package = crud.get_package_by_id(db, package_id)
        if not package:
            raise HTTPException(
                status_code=404,
                detail=f"Artifact with ID {id} not found"
            )
        
        # Get scores
        scores = crud.get_package_scores(db, package_id)
        if not scores:
            raise HTTPException(
                status_code=404,
                detail=f"No ratings found for artifact {id}"
            )
        
        # Return rating response
        return {
            "BusFactor": (
                scores.bus_factor if scores.bus_factor is not None else 0.0
            ),
            "BusFactorLatency": 0.0,  # Not tracked separately
            "Correctness": (
                scores.code_quality if scores.code_quality is not None else 0.0
            ),
            "CorrectnessLatency": 0.0,
            "RampUp": (
                scores.ramp_up_time if scores.ramp_up_time is not None else 0.0
            ),
            "RampUpLatency": 0.0,
            "ResponsiveMaintainer": (
                scores.performance_claims
                if scores.performance_claims is not None
                else 0.0
            ),
            "ResponsiveMaintainerLatency": 0.0,
            "LicenseScore": (
                scores.license_score
                if scores.license_score is not None
                else 0.0
            ),
            "LicenseScoreLatency": 0.0,
            "GoodPinningPractice": (
                scores.dataset_quality
                if scores.dataset_quality is not None
                else 0.0
            ),
            "GoodPinningPracticeLatency": 0.0,
            "PullRequest": (
                scores.reviewedness
                if scores.reviewedness is not None
                else 0.0
            ),
            "PullRequestLatency": 0.0,
            "NetScore": (
                scores.net_score if scores.net_score is not None else 0.0
            ),
            "NetScoreLatency": 0.0,
            "Reproducibility": (
                scores.reproducibility
                if scores.reproducibility is not None
                else 0.0
            ),
            "ReproducibilityLatency": 0.0,
        }
    
    # Get artifact by name endpoint (BASELINE)
    @app.get(
        "/artifact/byName/{name:path}",
        response_model=list[ArtifactMetadata],
        tags=["artifacts"]
    )
    def get_artifact_by_name(
        name: str,
        db: Session = Depends(get_db),
    ):
        """
        List artifact metadata for this name.
        
        Returns all artifacts (models, datasets, code) that match the
        given name. Multiple artifacts can share the same name but have
        different IDs.
        
        Note: Uses :path converter to allow names with slashes (/).
        
        Args:
            name: Artifact name to search for
            db: Database session
            
        Returns:
            List of artifact metadata entries matching the name
        """
        from fastapi import HTTPException
        
        # Search for packages with this exact name
        packages = db.query(Package).filter(Package.name == name).all()
        
        if not packages:
            raise HTTPException(
                status_code=404,
                detail=f"No artifact found with name: {name}"
            )
        
        # Return all matching artifacts
        results = []
        for pkg in packages:
            artifact_type = getattr(pkg, 'artifact_type', 'model')
            results.append(
                ArtifactMetadata(
                    name=pkg.name,
                    id=str(pkg.id),
                    type=artifact_type
                )
            )
        
        return results
    
    # Get artifact by type and ID endpoint (BASELINE)
    class Artifact(BaseModel):
        """Complete artifact with metadata and data."""
        metadata: ArtifactMetadata
        data: ArtifactData
    
    @app.get(
        "/artifacts/{artifact_type}/{id}",
        response_model=Artifact,
        tags=["artifacts"]
    )
    def get_artifact_by_id(
        artifact_type: str,
        id: str,
        db: Session = Depends(get_db),
    ):
        """
        Retrieve artifact by type and ID.
        
        Per OpenAPI spec: Returns artifact with metadata and data (url).
        
        Args:
            artifact_type: Type of artifact (model, dataset, code)
            id: Artifact ID
            db: Database session
            
        Returns:
            Artifact with metadata and data
        """
        from fastapi import HTTPException
        
        # Validate artifact type
        if artifact_type not in ["model", "dataset", "code"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid artifact type: {artifact_type}"
            )
        
        # Get package by ID
        try:
            package_id = int(id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid artifact ID format"
            )
        
        package = crud.get_package_by_id(db, package_id)
        if not package:
            raise HTTPException(
                status_code=404,
                detail=f"Artifact with ID {id} not found"
            )
        
        # Check if artifact type matches
        pkg_artifact_type = getattr(package, 'artifact_type', 'model')
        if pkg_artifact_type != artifact_type:
            raise HTTPException(
                status_code=404,
                detail=f"Artifact {id} is not of type {artifact_type}"
            )
        
        # Return artifact with metadata and data
        url = getattr(package, 'source_url', '')
        if not url:
            # Fallback to constructed URL if no source_url
            url = f"https://huggingface.co/{package.name}"
        
        return Artifact(
            metadata=ArtifactMetadata(
                name=package.name,
                id=str(package.id),
                type=pkg_artifact_type
            ),
            data=ArtifactData(url=url)
        )
    
    return app


# Create the app instance for uvicorn
app = create_app()

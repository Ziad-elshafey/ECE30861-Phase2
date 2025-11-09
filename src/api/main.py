"""Main FastAPI application factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
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
            "health": "/health",
            "frontend": "/frontend"
        }
    
    # Frontend endpoint for autograder
    @app.get("/frontend", response_class=HTMLResponse, tags=["frontend"])
    def frontend():
        """
        Simple frontend interface for the ML Model Registry.
        Provides a basic HTML page for interacting with the API.
        """
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ML Model Registry - Frontend</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                .container {
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 800px;
                    width: 100%;
                    padding: 40px;
                }
                h1 {
                    color: #667eea;
                    margin-bottom: 10px;
                    font-size: 2.5em;
                }
                .subtitle {
                    color: #666;
                    margin-bottom: 30px;
                    font-size: 1.1em;
                }
                .section {
                    margin: 30px 0;
                }
                .section h2 {
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 1.5em;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }
                .links {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-top: 20px;
                }
                .link-card {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-decoration: none;
                    transition: transform 0.2s, box-shadow 0.2s;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                }
                .link-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
                }
                .link-card h3 {
                    font-size: 1.2em;
                    margin-bottom: 10px;
                }
                .link-card p {
                    font-size: 0.9em;
                    opacity: 0.9;
                }
                .status {
                    display: inline-block;
                    background: #10b981;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    font-weight: bold;
                }
                .info-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin-top: 20px;
                }
                .info-card {
                    background: #f3f4f6;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                }
                .info-card strong {
                    display: block;
                    color: #667eea;
                    font-size: 2em;
                    margin-bottom: 5px;
                }
                .info-card span {
                    color: #666;
                    font-size: 0.9em;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 ML Model Registry</h1>
                <p class="subtitle">Trustworthy Machine Learning Model Management Platform</p>
                <p><span class="status">✓ System Online</span></p>
                
                <div class="section">
                    <h2>📊 Quick Stats</h2>
                    <div class="info-grid">
                        <div class="info-card">
                            <strong>8</strong>
                            <span>Quality Metrics</span>
                        </div>
                        <div class="info-card">
                            <strong>REST</strong>
                            <span>API Type</span>
                        </div>
                        <div class="info-card">
                            <strong>JWT</strong>
                            <span>Auth Method</span>
                        </div>
                        <div class="info-card">
                            <strong>AWS</strong>
                            <span>Cloud Provider</span>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔗 API Resources</h2>
                    <div class="links">
                        <a href="/docs" class="link-card">
                            <h3>📚 API Docs</h3>
                            <p>Interactive Swagger UI</p>
                        </a>
                        <a href="/redoc" class="link-card">
                            <h3>📖 ReDoc</h3>
                            <p>Alternative API docs</p>
                        </a>
                        <a href="/health" class="link-card">
                            <h3>💚 Health</h3>
                            <p>System status</p>
                        </a>
                        <a href="/tracks" class="link-card">
                            <h3>🛤️ Tracks</h3>
                            <p>Feature tracks</p>
                        </a>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🎯 Features</h2>
                    <ul style="list-style: none; padding-left: 0;">
                        <li style="padding: 10px 0; border-bottom: 1px solid #eee;">✓ User Authentication & Authorization (JWT)</li>
                        <li style="padding: 10px 0; border-bottom: 1px solid #eee;">✓ Package Upload & Management</li>
                        <li style="padding: 10px 0; border-bottom: 1px solid #eee;">✓ Quality Scoring (8 Metrics)</li>
                        <li style="padding: 10px 0; border-bottom: 1px solid #eee;">✓ HuggingFace Model Ingestion</li>
                        <li style="padding: 10px 0; border-bottom: 1px solid #eee;">✓ Regex Search & Filtering</li>
                        <li style="padding: 10px 0;">✓ System Health Monitoring</li>
                    </ul>
                </div>
                
                <div class="section" style="text-align: center; padding-top: 20px; border-top: 2px solid #eee;">
                    <p style="color: #666;">
                        <strong>Team 20</strong> | Ahmed Elbehiry • Zeyad Elshafey • Omar Ahmed • Jacob Walter
                    </p>
                    <p style="color: #999; margin-top: 10px; font-size: 0.9em;">
                        ECE30861 - Software Engineering | Purdue University
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
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
        - Access control track: Complete user authentication and authorization system
          * User registration and login with JWT tokens
          * Role-based permissions (admin, upload, download, search)
          * Secure password hashing with bcrypt
          * Token-based authentication for API endpoints
          * User account management (create, read, update, delete)
        
        Returns:
            Object with plannedTracks array matching OpenAPI spec enum values
        """
        return {
            "plannedTracks": ["Access control track"]
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
        Supports regex patterns for name matching.
        
        Args:
            queries: List of artifact queries
            offset: Pagination offset
            db: Database session
            
        Returns:
            List of matching artifact metadata
        """
        from src.database.models import Package
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
                # Search by name with regex support
                packages = crud.get_packages(
                    db, 
                    skip=0, 
                    limit=1000,
                    name_filter=query.name,
                    use_regex=True
                )
                
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

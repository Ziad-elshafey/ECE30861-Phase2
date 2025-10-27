"""
Main entry point for the ML Model Registry API.

Run with: python main.py
Or with uvicorn: uvicorn main:app --reload
"""

from src.api.main import create_app

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )

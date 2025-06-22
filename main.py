import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import router
from app.database import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="API for Events Articles Chatbot with data fetching, SQLite storage, and ChromaDB embeddings",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["data"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting up Events Articles Chatbot API...")
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Events Articles Chatbot API",
        "version": settings.app_version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

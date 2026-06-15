"""
RegRadar FastAPI Application
Main entry point for the backend API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from .config import settings
from .database import init_db
from .routes import auth_router, search_router, chat_router, circulars_router
from .schemas import HealthResponse
from .models import User, Circular  # Import models so they're registered with Base

# Create FastAPI app
app = FastAPI(
    title="RegRadar API",
    description="AI-Powered Regulatory Intelligence Platform for RBI & SEBI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("[INFO] Starting RegRadar API...")
    print(f"[INFO] Environment: {settings.environment}")
    await init_db()
    print("[INFO] Database initialized")


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns API status and environment info
    """
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
        database="connected",
        timestamp=datetime.utcnow()
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": "RegRadar API - AI-Powered Regulatory Intelligence",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(auth_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(circulars_router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.environment == "development" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development"
    )

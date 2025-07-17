"""
ManipulatorAI FastAPI Application - Simplified Startup
Main application entry point with Azure OpenAI integration focus
"""

import time
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Core imports
from app.core.config import settings
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API routers
from app.api import ai_testing_simple

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Simplified application lifespan management
    """
    # Startup
    logger.info("🚀 ManipulatorAI application starting up...")
    
    try:
        logger.info("✅ Application startup completed")
        yield
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise
    
    # Shutdown
    logger.info("🛑 Application shutting down...")
    logger.info("✅ Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="ManipulatorAI",
    description="""
    ## 🤖 ManipulatorAI: AI-Powered Conversation Platform
    
    A sophisticated AI system that intelligently processes customer interactions 
    and generates contextual, persuasive responses for business conversations.
    
    ### 🚀 Key Features
    
    * **AI-Powered Conversations** - Azure OpenAI integration for natural responses
    * **Keyword Extraction** - Intelligent product keyword detection
    * **Conversation Branches** - Convincer and Manipulator conversation flows
    * **Real-time Processing** - Async processing for optimal performance
    
    ### 🧪 Testing Endpoints
    
    This simplified version focuses on Azure OpenAI testing endpoints:
    - `/ai/extract-keywords` - Test keyword extraction
    - `/ai/full-pipeline` - Test complete AI pipeline
    
    ### 🔧 Technology Stack
    
    * **FastAPI** - High-performance async web framework
    * **Azure OpenAI** - Advanced AI conversation capabilities
    * **Async/Await** - Optimized for concurrent processing
    
    ## Quick Start
    
    1. Ensure Azure OpenAI credentials are configured in `.env`
    2. Access API documentation: `/docs`
    3. Test AI integration: `/ai/extract-keywords`
    
    ## Support
    
    For support and documentation, visit the project repository.
    """,
    version="1.0.0",
    contact={
        "name": "ManipulatorAI Team",
        "email": "support@manipulator-ai.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# Request/Response logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Log all requests and responses with performance metrics
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"📨 {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"💥 {request.method} {request.url.path} - ERROR - {process_time:.3f}s: {e}")
        raise


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path),
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "ManipulatorAI",
        "version": "1.0.0",
        "timestamp": time.time(),
        "azure_openai_configured": bool(settings.azure_openai_api_key and 
                                          settings.azure_openai_api_key != "your_azure_openai_api_key_here")
    }

# Status endpoint
@app.get("/status", tags=["Health"])
async def status():
    """
    Detailed status endpoint
    """
    return {
        "service": "ManipulatorAI",
        "status": "operational",
        "version": "1.0.0",
        "environment": settings.app_env,
        "debug_mode": settings.debug,
        "azure_openai": {
            "configured": bool(settings.azure_openai_api_key and 
                             settings.azure_openai_api_key != "your_azure_openai_api_key_here"),
            "endpoint": settings.azure_openai_endpoint,
            "deployment": settings.azure_openai_deployment_name,
            "api_version": settings.azure_openai_api_version
        },
        "features": {
            "keyword_extraction": True,
            "conversation_generation": True,
            "ai_pipeline": True
        }
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint with service information
    """
    return {
        "message": "🤖 Welcome to ManipulatorAI API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "status": "/status",
        "features": [
            "AI-powered conversation processing",
            "Azure OpenAI integration", 
            "Keyword extraction",
            "Conversation generation",
            "Real-time analytics"
        ],
        "endpoints": {
            "ai_testing": "/ai",
            "health": "/health",
            "status": "/status",
            "docs": "/docs"
        }
    }

# Include API routers
app.include_router(ai_testing_simple.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_simple:app", 
        host=settings.app_host, 
        port=settings.app_port, 
        reload=settings.debug
    )

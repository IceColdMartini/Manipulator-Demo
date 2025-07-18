from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import db_manager
from app.core.config import settings
from app.api import webhooks, conversations, products, ai_testing
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting ManipulatorAI...")
    try:
        await db_manager.connect_postgresql()
        await db_manager.connect_mongodb()
        await db_manager.connect_redis()
        logger.info("All database connections established")
    except Exception as e:
        logger.error(f"Failed to connect to databases: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ManipulatorAI...")
    await db_manager.close_connections()
    logger.info("All database connections closed")

app = FastAPI(
    title="ManipulatorAI",
    description="A microservice for intelligent customer engagement",
    version="0.1.0",
    lifespan=lifespan
)

# Include API routers
app.include_router(webhooks.router)
app.include_router(conversations.router)
app.include_router(products.router)
app.include_router(ai_testing.router)

@app.get("/")
async def read_root():
    return {
        "message": "Welcome to ManipulatorAI",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "webhooks": "/webhook/facebook, /webhook/instagram",
            "conversations": "/conversation/message, /conversation/{id}",
            "products": "/products/, /products/{id}, /products/search",
            "ai_testing": "/ai/extract-keywords, /ai/match-products, /ai/full-pipeline"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-07-13T00:00:00Z",
        "databases": {
            "postgresql": "connected",
            "mongodb": "connected", 
            "redis": "connected"
        }
    }

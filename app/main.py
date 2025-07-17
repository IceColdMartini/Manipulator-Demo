"""
ManipulatorAI FastAPI Application
Main application entry point with comprehensive logging, error handling, and monitoring
"""

import time
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# Core imports
from app.core.config import settings
from app.core.logging import (
    logger_manager, 
    main_logger as logger,
    api_logger,
    performance_logger
)
from app.core.error_handling import (
    error_handler,
    ValidationError,
    ConversationError,
    DatabaseError,
    ExternalAPIError,
    TaskProcessingError,
    validation_exception_handler,
    conversation_exception_handler,
    database_exception_handler,
    external_api_exception_handler,
    task_processing_exception_handler,
    general_exception_handler
)

# Database connections
from app.core.database import get_mongo_db, get_postgres_db
from app.core.redis_client import get_redis_client

# API routers
from app.api import conversations

# Services
from app.services.task_manager import task_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 ManipulatorAI application starting up...")
    
    try:
        # Initialize database connections
        logger.info("Initializing database connections...")
        
        # Test MongoDB connection
        try:
            mongo_db = await anext(get_mongo_db())
            await mongo_db.command("ping")
            logger.info("✅ MongoDB connection established")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
        
        # Test Redis connection
        try:
            redis_client = await anext(get_redis_client())
            await redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
        
        # Initialize task manager
        logger.info("Initializing task manager...")
        # Task manager is already initialized on import
        logger.info("✅ Task manager initialized")
        
        # Log application startup
        logger.info("✅ ManipulatorAI application startup completed successfully")
        logger.info(f"🔧 Environment: {settings.APP_ENV}")
        logger.info(f"🐛 Debug mode: {settings.DEBUG}")
        
        yield
        
    except Exception as e:
        logger.critical(f"💥 Application startup failed: {e}")
        raise
    
    # Shutdown
    logger.info("🛑 ManipulatorAI application shutting down...")
    
    try:
        # Cleanup resources
        logger.info("Cleaning up resources...")
        
        # Close database connections if needed
        # await close_database_connections()
        
        logger.info("✅ Application shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during application shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="ManipulatorAI",
    description="""
    🤖 **ManipulatorAI** - Advanced AI-powered conversation manipulation and webhook processing platform
    
    ## Features
    
    * **🔄 Asynchronous Task Processing** - Redis-backed Celery task queue for responsive API
    * **💬 Intelligent Conversations** - AI-powered conversation manipulation and engagement
    * **🌐 Multi-Platform Webhooks** - Facebook, Instagram, Google, and custom webhook integration
    * **📊 Real-time Analytics** - Comprehensive conversation and performance analytics
    * **🛡️ Robust Error Handling** - Comprehensive error handling with recovery mechanisms
    * **📈 Performance Monitoring** - Real-time task and queue monitoring with Flower
    * **🐳 Containerized Deployment** - Docker and Docker Compose ready for production
    
    ## Architecture
    
    * **FastAPI** - High-performance async web framework
    * **Celery + Redis** - Distributed task queue for async processing
    * **MongoDB** - Conversation and analytics data storage
    * **PostgreSQL** - Structured data and user management
    * **OpenAI/Azure OpenAI** - Advanced AI conversation capabilities
    
    ## Quick Start
    
    1. Configure your environment variables in `.env`
    2. Start services: `./scripts/deploy.sh deploy`
    3. Access API documentation: `/docs`
    4. Monitor tasks: `/flower` (port 5555)
    
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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# Request/Response logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Log all HTTP requests and responses with performance metrics
    """
    start_time = time.time()
    
    # Log request
    api_logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Log response
        api_logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": duration
            }
        )
        
        # Log performance metric
        performance_logger.info(
            f"API response time: {request.method} {request.url.path}",
            extra={
                "metric_name": "api_response_time",
                "value": duration,
                "unit": "ms",
                "endpoint": f"{request.method} {request.url.path}",
                "status_code": response.status_code
            }
        )
        
        return response
        
    except Exception as e:
        # Calculate duration even for errors
        duration = (time.time() - start_time) * 1000
        
        # Log error
        api_logger.error(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration": duration,
                "error": str(e)
            }
        )
        
        # Re-raise the exception
        raise


# Exception handlers
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(ConversationError, conversation_exception_handler)
app.add_exception_handler(DatabaseError, database_exception_handler)
app.add_exception_handler(ExternalAPIError, external_api_exception_handler)
app.add_exception_handler(TaskProcessingError, task_processing_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Comprehensive health check endpoint
    Checks all critical system components
    """
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "components": {}
    }
    
    try:
        # Check MongoDB
        try:
            mongo_db = await anext(get_mongo_db())
            await mongo_db.command("ping")
            health_status["components"]["mongodb"] = {"status": "healthy", "response_time": None}
        except Exception as e:
            health_status["components"]["mongodb"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check Redis
        try:
            redis_client = await anext(get_redis_client())
            redis_start = time.time()
            await redis_client.ping()
            redis_time = (time.time() - redis_start) * 1000
            health_status["components"]["redis"] = {"status": "healthy", "response_time": redis_time}
        except Exception as e:
            health_status["components"]["redis"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check task queue (Celery)
        try:
            # Basic check - we can expand this to actually ping workers
            queue_stats = task_manager.get_queue_stats()
            health_status["components"]["task_queue"] = {
                "status": "healthy", 
                "active_tasks": sum(stats.get("active", 0) for stats in queue_stats.values())
            }
        except Exception as e:
            health_status["components"]["task_queue"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # Overall response time
        health_status["response_time"] = (time.time() - start_time) * 1000
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


# System status endpoint
@app.get("/status", tags=["Health"])
async def system_status():
    """
    Detailed system status including task queue statistics
    """
    try:
        # Get task queue statistics
        queue_stats = task_manager.get_queue_stats()
        active_tasks = task_manager.get_active_tasks()
        error_stats = error_handler.get_error_statistics()
        
        return {
            "system": {
                "status": "operational",
                "environment": settings.APP_ENV,
                "debug_mode": settings.DEBUG,
                "version": "1.0.0"
            },
            "task_queues": queue_stats,
            "active_tasks": {
                "count": len(active_tasks),
                "tasks": active_tasks[:10]  # Show first 10 for brevity
            },
            "error_statistics": error_stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve system status")


# API version info
@app.get("/version", tags=["Health"])
async def version_info():
    """
    API version and build information
    """
    return {
        "version": "1.0.0",
        "api_version": "v1",
        "build_date": "2025-07-15",
        "environment": settings.APP_ENV,
        "features": {
            "async_processing": True,
            "webhook_integration": True,
            "conversation_ai": True,
            "analytics": True,
            "monitoring": True
        }
    }


# Include API routers
app.include_router(
    conversations.router,
    prefix="/api/v1/conversations",
    tags=["Conversations"]
)


# Custom OpenAPI schema
def custom_openapi():
    """
    Custom OpenAPI schema with enhanced documentation
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ManipulatorAI API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom schema components
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Root endpoint with API information
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
            "AI-powered conversation manipulation",
            "Multi-platform webhook processing", 
            "Asynchronous task processing",
            "Real-time analytics",
            "Comprehensive monitoring"
        ],
        "endpoints": {
            "conversations": "/api/v1/conversations",
            "health": "/health",
            "status": "/status",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting ManipulatorAI application...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_config=None,  # Use our custom logging
        access_log=False  # We handle access logging in middleware
    )

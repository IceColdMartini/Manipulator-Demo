"""
Database initialization script
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from src.core.config import get_settings
from src.models.tables import metadata
from src.database.postgres import engine as postgres_engine
from src.database.mongodb import mongodb
from src.database.redis import get_redis_client

settings = get_settings()
logger = logging.getLogger(__name__)

async def create_postgres_database():
    """Create PostgreSQL database if it doesn't exist"""
    # Connect to default database to create our app database
    default_engine = create_async_engine(
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/postgres"
    )
    
    try:
        async with default_engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}'")
            )
            exists = result.scalar() is not None
            
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{settings.POSTGRES_DB}"'))
                logger.info(f"Created database {settings.POSTGRES_DB}")
    except Exception as e:
        logger.error(f"Error creating database: {e}")
    finally:
        await default_engine.dispose()

async def init_postgres():
    """Initialize PostgreSQL schema"""
    try:
        async with postgres_engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        logger.info("PostgreSQL tables created successfully")
    except Exception as e:
        logger.error(f"Error creating PostgreSQL tables: {e}")

async def init_mongodb():
    """Initialize MongoDB collections and indexes"""
    try:
        # Create indexes for conversations collection
        await mongodb.conversations.create_index([("user_id", 1)])
        await mongodb.conversations.create_index([("created_at", -1)])
        
        # Create indexes for user_interactions collection
        await mongodb.user_interactions.create_index([("user_id", 1)])
        await mongodb.user_interactions.create_index([("interaction_type", 1)])
        await mongodb.user_interactions.create_index([("created_at", -1)])
        
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {e}")

async def init_redis():
    """Test Redis connection"""
    try:
        async for redis in get_redis_client():
            await redis.ping()
            logger.info("Redis connection successful")
            break
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")

async def init_all():
    """Initialize all databases"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and initialize PostgreSQL
    await create_postgres_database()
    await init_postgres()
    
    # Initialize MongoDB
    await init_mongodb()
    
    # Test Redis connection
    await init_redis()

if __name__ == "__main__":
    asyncio.run(init_all())

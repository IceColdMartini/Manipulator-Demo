from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as aioredis
from app.core.config import settings
from app.models.database import Base
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        # PostgreSQL setup
        self.postgres_engine = None
        self.postgres_session = None
        
        # MongoDB setup
        self.mongo_client = None
        self.mongo_db = None
        
        # Redis setup
        self.redis_client = None
    
    async def connect_postgresql(self):
        """Initialize PostgreSQL connection"""
        try:
            # Convert postgresql:// to postgresql+asyncpg:// for async support
            async_url = settings.postgresql_url.replace("postgresql://", "postgresql+asyncpg://")
            
            self.postgres_engine = create_async_engine(
                async_url,
                echo=settings.debug,
                pool_pre_ping=True
            )
            
            # Create async session factory
            self.postgres_session = sessionmaker(
                self.postgres_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("PostgreSQL connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def connect_mongodb(self):
        """Initialize MongoDB connection"""
        try:
            self.mongo_client = AsyncIOMotorClient(settings.mongodb_url)
            self.mongo_db = self.mongo_client.get_database("manipulator_conversations")
            
            # Test connection
            await self.mongo_client.admin.command('ping')
            logger.info("MongoDB connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def connect_redis(self):
        """Initialize Redis connection"""
        try:
            redis_url = f"redis://"
            if settings.redis_password:
                redis_url += f":{settings.redis_password}@"
            redis_url += f"{settings.redis_host}:{settings.redis_port}"
            
            self.redis_client = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def create_tables(self):
        """Create database tables"""
        try:
            async with self.postgres_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    async def close_connections(self):
        """Close all database connections"""
        if self.postgres_engine:
            await self.postgres_engine.dispose()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("All database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

# Dependency functions for FastAPI
async def get_postgres_session():
    """Dependency to get PostgreSQL session"""
    async with db_manager.postgres_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_mongo_db():
    """Dependency to get MongoDB database"""
    return db_manager.mongo_db

async def get_redis_client():
    """Dependency to get Redis client"""
    return db_manager.redis_client

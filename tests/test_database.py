"""
Test database connections
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from src.database.postgres import get_postgres_db
from src.database.mongodb import get_mongodb_db
from src.database.redis import get_redis_client

@pytest.mark.asyncio
async def test_postgres_connection():
    """Test PostgreSQL connection"""
    async for db in get_postgres_db():
        assert isinstance(db, AsyncSession)
        break

@pytest.mark.asyncio
async def test_mongodb_connection():
    """Test MongoDB connection"""
    db = await get_mongodb_db()
    assert isinstance(db, AsyncIOMotorDatabase)

@pytest.mark.asyncio
async def test_redis_connection():
    """Test Redis connection"""
    async for redis in get_redis_client():
        assert isinstance(redis, Redis)
        await redis.ping()
        break

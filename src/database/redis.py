"""
Redis connection management
"""
from typing import AsyncGenerator
from redis.asyncio import Redis, ConnectionPool
from src.core.config import get_settings

settings = get_settings()

# Create Redis connection pool
redis_pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    retry_on_timeout=True,
    socket_keepalive=True,
    health_check_interval=30
)

async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """
    Dependency function that yields Redis clients
    """
    client = Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.close()

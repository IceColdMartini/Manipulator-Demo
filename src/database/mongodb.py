"""
MongoDB database connection management
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.core.config import get_settings

settings = get_settings()

# Create MongoDB client
client = AsyncIOMotorClient(settings.MONGODB_URL)
mongodb = client[settings.MONGODB_DB]

async def get_mongodb_db() -> AsyncIOMotorDatabase:
    """
    Dependency function that returns MongoDB database instance
    """
    return mongodb

# Collections
conversations = mongodb.conversations
user_interactions = mongodb.user_interactions
social_media_events = mongodb.social_media_events

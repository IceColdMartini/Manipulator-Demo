#!/usr/bin/env python3
"""
Fresh database integration test with reloaded configuration
"""

import asyncio
import sys
import os
from pathlib import Path

# Force environment reload
os.environ.clear()
from dotenv import load_dotenv
load_dotenv('.env', override=True)

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import after environment is set
from app.core.config import Settings
from app.core.database import DatabaseManager
from app.services.product_service import ProductService
from app.services.conversation_service import ConversationService
from app.models.schemas import ProductCreate, ProductAttributes, ConversationCreate, ConversationBranch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create fresh settings and database manager
settings = Settings()
db_manager = DatabaseManager()

async def test_postgresql():
    """Test PostgreSQL connection and product operations"""
    logger.info("Testing PostgreSQL connection...")
    logger.info(f"Using PostgreSQL URL: {settings.postgresql_url}")
    
    try:
        await db_manager.connect_postgresql()
        
        async with db_manager.postgres_session() as session:
            product_service = ProductService(session)
            
            # Test getting all products
            products = await product_service.get_all_products()
            logger.info(f"Found {len(products)} products in database")
            
            if products:
                # Test getting a specific product
                first_product = products[0]
                retrieved_product = await product_service.get_product_by_id(first_product.product_id)
                logger.info(f"Retrieved product: {retrieved_product.product_description[:50]}...")
                
                # Test tag-based search
                keywords = ["demo", "product"]
                matches = await product_service.search_products_by_tags(keywords, threshold=0.3)
                logger.info(f"Found {len(matches)} products matching keywords: {keywords}")
        
        logger.info("✅ PostgreSQL tests passed")
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL test failed: {e}")
        raise

async def test_mongodb():
    """Test MongoDB connection and conversation operations"""
    logger.info("Testing MongoDB connection...")
    logger.info(f"Using MongoDB URL: {settings.mongodb_url}")
    
    try:
        await db_manager.connect_mongodb()
        
        conversation_service = ConversationService(db_manager.mongo_db)
        
        # Test creating a conversation
        conversation_data = ConversationCreate(
            customer_id="test_customer_123",
            business_id="test_business_456", 
            product_context=["test_product_789"],
            conversation_branch=ConversationBranch.MANIPULATOR
        )
        
        conversation = await conversation_service.create_conversation(conversation_data)
        logger.info(f"Created test conversation: {conversation.conversation_id}")
        
        # Test retrieving the conversation
        retrieved = await conversation_service.get_conversation(conversation.conversation_id)
        if retrieved:
            logger.info(f"Retrieved conversation for customer: {retrieved.customer_id}")
        
        logger.info("✅ MongoDB tests passed")
        
    except Exception as e:
        logger.error(f"❌ MongoDB test failed: {e}")
        raise

async def test_redis():
    """Test Redis connection"""
    logger.info("Testing Redis connection...")
    logger.info(f"Using Redis host: {settings.redis_host}:{settings.redis_port}")
    
    try:
        await db_manager.connect_redis()
        
        # Test basic Redis operations
        await db_manager.redis_client.set("test_key", "test_value")
        value = await db_manager.redis_client.get("test_key")
        
        if value == "test_value":
            logger.info("✅ Redis tests passed")
        else:
            raise Exception("Redis value mismatch")
        
        # Clean up test key
        await db_manager.redis_client.delete("test_key")
        
    except Exception as e:
        logger.error(f"❌ Redis test failed: {e}")
        raise

async def main():
    """Run all tests"""
    logger.info("Starting fresh database integration tests...")
    
    try:
        await test_postgresql()
        await test_mongodb()
        await test_redis()
        
        logger.info("🎉 All database integration tests passed!")
        
    except Exception as e:
        logger.error(f"💥 Tests failed: {e}")
        sys.exit(1)
    finally:
        await db_manager.close_connections()

if __name__ == "__main__":
    asyncio.run(main())

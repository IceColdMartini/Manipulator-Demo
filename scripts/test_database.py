#!/usr/bin/env python3
"""
Test script to verify database connections and basic functionality
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import db_manager
from app.services.product_service import ProductService
from app.services.conversation_service import ConversationService
from app.models.schemas import ProductCreate, ProductAttributes, ConversationCreate, ConversationBranch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_postgresql():
    """Test PostgreSQL connection and product operations"""
    logger.info("Testing PostgreSQL connection...")
    
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
                keywords = ["smartphone", "mobile"]
                matches = await product_service.search_products_by_tags(keywords, threshold=0.3)
                logger.info(f"Found {len(matches)} products matching keywords: {keywords}")
        
        logger.info("✅ PostgreSQL tests passed")
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL test failed: {e}")
        raise

async def test_mongodb():
    """Test MongoDB connection and conversation operations"""
    logger.info("Testing MongoDB connection...")
    
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
    logger.info("Starting database integration tests...")
    
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

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
        
        async with db_manager.get_postgres_session() as session:
            product_service = ProductService(session)
            
            # Create a sample product for testing
            product_data = ProductCreate(
                name="Test Product",
                description="A product for testing purposes",
                price=99.99,
                currency="USD",
                category="Testing",
                metadata={"test": "true"}
            )
            created_product = await product_service.create_product(product_data)
            logger.info(f"Created test product: {created_product.name}")

            # Test getting all products
            products = await product_service.get_all_products()
            logger.info(f"Found {len(products)} products in database")
            
            assert len(products) > 0, "No products found in the database."

            # Test getting a specific product
            retrieved_product = await product_service.get_product_by_id(created_product.id)
            logger.info(f"Retrieved product: {retrieved_product.description}")
            assert retrieved_product is not None, "Failed to retrieve the created product."
            
            # Test searching for the product
            search_results = await product_service.search_products_by_keywords(keywords=["Test Product"])
            logger.info(f"Found {len(search_results)} products matching keywords: ['Test Product']")
            assert len(search_results) > 0, "Failed to find the product by search."

        logger.info("✅ PostgreSQL tests passed")
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL tests failed: {e}")
        raise

async def test_mongodb():
    """Test MongoDB connection and conversation operations"""
    logger.info("Testing MongoDB connection...")
    
    try:
        await db_manager.connect_mongodb()
        
        mongo_db = db_manager.get_mongo_db()
        conversation_service = ConversationService(mongo_db)
        
        # Create a sample conversation
        conversation_data = ConversationCreate(
            customer_id="test_customer_123",
            business_id="test_business_456",
            product_context=[],
            conversation_branch="manipulator"
        )
        created_conversation = await conversation_service.create_conversation(conversation_data)
        logger.info(f"Created test conversation: {created_conversation.conversation_id}")
        
        # Retrieve the conversation
        retrieved_conversation = await conversation_service.get_conversation_by_id(created_conversation.conversation_id)
        logger.info(f"Retrieved conversation for customer: {retrieved_conversation.customer_id}")
        assert retrieved_conversation is not None, "Failed to retrieve the created conversation."

        logger.info("✅ MongoDB tests passed")
        
    except Exception as e:
        logger.error(f"❌ MongoDB test failed: {e}")
        raise

async def test_redis():
    """Test Redis connection"""
    logger.info("Testing Redis connection...")
    
    try:
        await db_manager.connect_redis()
        redis_client = db_manager.get_redis_client()
        
        # Test setting and getting a key
        await redis_client.set("test_key", "test_value")
        value = await redis_client.get("test_key")
        
        assert value == "test_value", "Redis SET/GET operation failed."
        logger.info("✅ Redis tests passed")
        
    except Exception as e:
        logger.error(f"❌ Redis tests failed: {e}")
        raise

async def main():
    """Run all database integration tests"""
    logger.info("Starting database integration tests...")
    try:
        await test_postgresql()
        await test_mongodb()
        await test_redis()
        logger.info("🎉 All database integration tests passed!")
    except Exception as e:
        logger.error(f"🔥 Database integration tests failed: {e}")
    finally:
        await db_manager.close_connections()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

#!/usr/bin/env python3
"""
Database setup script for ManipulatorAI
This script initializes the PostgreSQL database and creates the required tables.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import db_manager
from app.core.config import settings
from app.models.database import Base
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def create_database_tables():
    """Create all database tables"""
    try:
        logger.info("Starting database setup...")
        
        # Connect to PostgreSQL
        await db_manager.connect_postgresql()
        logger.info("Connected to PostgreSQL")
        
        # Create tables
        await db_manager.create_tables()
        logger.info("Database tables created successfully")
        
        # Test MongoDB connection
        await db_manager.connect_mongodb()
        logger.info("Connected to MongoDB")
        
        # Test Redis connection
        await db_manager.connect_redis()
        logger.info("Connected to Redis")
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)
    finally:
        await db_manager.close_connections()

async def insert_sample_products():
    """Insert sample products for testing"""
    try:
        await db_manager.connect_postgresql()
        
        from app.models.database import ProductModel
        from sqlalchemy import text
        
        async with db_manager.postgres_session() as session:
            # Sample products
            sample_products = [
                {
                    "product_attributes": {
                        "price": "$299.99",
                        "color": "Black",
                        "category": "Electronics",
                        "brand": "TechCorp"
                    },
                    "product_tag": ["smartphone", "mobile", "tech", "communication", "android"],
                    "product_description": "Advanced Android smartphone with 5G connectivity, triple camera system, and long-lasting battery. Perfect for communication and entertainment."
                },
                {
                    "product_attributes": {
                        "price": "$599.99", 
                        "color": "Silver",
                        "category": "Electronics",
                        "brand": "TechCorp"
                    },
                    "product_tag": ["laptop", "computer", "productivity", "work", "portable"],
                    "product_description": "Lightweight laptop with powerful processor, perfect for work and productivity. Features long battery life and premium build quality."
                },
                {
                    "product_attributes": {
                        "price": "$149.99",
                        "color": "Blue",
                        "category": "Electronics", 
                        "brand": "TechCorp"
                    },
                    "product_tag": ["headphones", "audio", "wireless", "music", "noise-canceling"],
                    "product_description": "Premium wireless headphones with active noise cancellation. Delivers exceptional audio quality for music lovers and professionals."
                },
                {
                    "product_attributes": {
                        "price": "$79.99",
                        "color": "White",
                        "category": "Fashion",
                        "brand": "StyleCorp"
                    },
                    "product_tag": ["shirt", "clothing", "casual", "cotton", "fashion"],
                    "product_description": "Comfortable cotton casual shirt, perfect for everyday wear. Made from premium materials with a modern fit."
                }
            ]
            
            for product_data in sample_products:
                product = ProductModel(
                    product_attributes=product_data["product_attributes"],
                    product_tag=product_data["product_tag"],
                    product_description=product_data["product_description"]
                )
                session.add(product)
            
            await session.commit()
            logger.info(f"Inserted {len(sample_products)} sample products")
            
    except Exception as e:
        logger.error(f"Failed to insert sample products: {e}")
        raise
    finally:
        await db_manager.close_connections()

async def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--with-samples":
        logger.info("Setting up database with sample data...")
        await create_database_tables()
        await insert_sample_products()
    else:
        logger.info("Setting up database...")
        await create_database_tables()
        logger.info("To add sample products, run: python setup_database.py --with-samples")

if __name__ == "__main__":
    asyncio.run(main())

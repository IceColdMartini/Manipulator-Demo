#!/usr/bin/env python3
"""
Quick API test to verify product search functionality
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from app.core.database import db_manager
from app.services.product_service import ProductService

async def test_product_search_api():
    """Test the product search functionality that will be used by tagMatcher"""
    print("🔍 Testing Product Search API functionality...")
    
    try:
        await db_manager.connect_postgresql()
        
        async with db_manager.postgres_session() as session:
            product_service = ProductService(session)
            
            # Test 1: Search for electronics
            print("\n📱 Test 1: Searching for 'smartphone' and 'mobile'")
            keywords = ["smartphone", "mobile"]
            matches = await product_service.search_products_by_tags(keywords, threshold=0.3)
            
            for match in matches:
                product = match['product']
                print(f"   ✅ Found: {product.product_description[:50]}... (Score: {match['score']:.2f})")
            
            # Test 2: Search for laptops 
            print("\n💻 Test 2: Searching for 'laptop' and 'computer'")
            keywords = ["laptop", "computer"]
            matches = await product_service.search_products_by_tags(keywords, threshold=0.3)
            
            for match in matches:
                product = match['product']
                print(f"   ✅ Found: {product.product_description[:50]}... (Score: {match['score']:.2f})")
            
            # Test 3: Search for audio products
            print("\n🎧 Test 3: Searching for 'audio' and 'music'")
            keywords = ["audio", "music"]
            matches = await product_service.search_products_by_tags(keywords, threshold=0.3)
            
            for match in matches:
                product = match['product']
                print(f"   ✅ Found: {product.product_description[:50]}... (Score: {match['score']:.2f})")
            
            # Test 4: Search for fashion items
            print("\n👕 Test 4: Searching for 'clothing' and 'fashion'")
            keywords = ["clothing", "fashion"]
            matches = await product_service.search_products_by_tags(keywords, threshold=0.3)
            
            for match in matches:
                product = match['product']
                print(f"   ✅ Found: {product.product_description[:50]}... (Score: {match['score']:.2f})")
            
            print("\n🎯 tagMatcher simulation successful! This is exactly how the system will work:")
            print("   1. keyRetriever extracts keywords from user message")
            print("   2. tagMatcher finds matching products using these keywords")
            print("   3. Conversation engine gets product context for LLM")
            
    except Exception as e:
        print(f"❌ Product search test failed: {e}")
        raise
    finally:
        await db_manager.close_connections()

if __name__ == "__main__":
    asyncio.run(test_product_search_api())

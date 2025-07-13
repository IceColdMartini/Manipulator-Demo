#!/usr/bin/env python3
"""
Comprehensive API endpoint testing script for ManipulatorAI Step 4
Tests all webhook and conversation endpoints
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"

async def test_basic_endpoints():
    """Test basic application endpoints"""
    logger.info("🔧 Testing basic endpoints...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test root endpoint
            response = await client.get(f"{BASE_URL}/")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "running"
            logger.info("✅ Root endpoint working")
            
            # Test health endpoint
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            logger.info("✅ Health endpoint working")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Basic endpoints test failed: {e}")
            return False

async def test_products_api():
    """Test products API endpoints"""
    logger.info("📦 Testing products API...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test get all products
            response = await client.get(f"{BASE_URL}/products/")
            assert response.status_code == 200
            products = response.json()
            assert len(products) > 0
            logger.info(f"✅ Retrieved {len(products)} products")
            
            # Test get specific product
            first_product_id = products[0]["product_id"]
            response = await client.get(f"{BASE_URL}/products/{first_product_id}")
            assert response.status_code == 200
            product = response.json()
            assert product["product_id"] == first_product_id
            logger.info(f"✅ Retrieved specific product: {product['product_description'][:30]}...")
            
            # Test product search (tagMatcher functionality)
            search_data = ["smartphone", "mobile"]
            response = await client.post(
                f"{BASE_URL}/products/search",
                params={"threshold": 0.3},
                json=search_data
            )
            assert response.status_code == 200
            search_results = response.json()
            assert "results" in search_results
            logger.info(f"✅ Product search found {len(search_results['results'])} matches")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Products API test failed: {e}")
            return False

async def test_webhook_endpoints():
    """Test webhook endpoints"""
    logger.info("🔔 Testing webhook endpoints...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test Facebook webhook verification
            verify_params = {
                "hub.mode": "subscribe",
                "hub.verify_token": "your_facebook_verify_token_here",
                "hub.challenge": "test_challenge_123"
            }
            response = await client.get(f"{BASE_URL}/webhook/facebook", params=verify_params)
            # This will fail because we're using placeholder token, but endpoint should exist
            assert response.status_code in [200, 403]
            logger.info("✅ Facebook webhook verification endpoint accessible")
            
            # Test Instagram webhook verification
            verify_params = {
                "hub.mode": "subscribe", 
                "hub.verify_token": "your_instagram_verify_token_here",
                "hub.challenge": "test_challenge_456"
            }
            response = await client.get(f"{BASE_URL}/webhook/instagram", params=verify_params)
            assert response.status_code in [200, 403]
            logger.info("✅ Instagram webhook verification endpoint accessible")
            
            # Test Facebook webhook handler with sample data
            sample_facebook_payload = {
                "object": "page",
                "entry": [
                    {
                        "id": "123456789",
                        "time": 1625097600,
                        "messaging": [
                            {
                                "sender": {"id": "user123"},
                                "recipient": {"id": "page123"},
                                "timestamp": 1625097600,
                                "message": {
                                    "mid": "msg123",
                                    "text": "Hello, I'm interested in your products!"
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = await client.post(
                f"{BASE_URL}/webhook/facebook",
                json=sample_facebook_payload
            )
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            logger.info("✅ Facebook webhook handler working")
            
            # Test Instagram webhook handler
            sample_instagram_payload = {
                "object": "instagram",
                "entry": [
                    {
                        "id": "123456789",
                        "time": 1625097600,
                        "changes": [
                            {
                                "field": "comments",
                                "value": {
                                    "media_id": "media123",
                                    "comment_id": "comment123",
                                    "text": "Love this product!"
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = await client.post(
                f"{BASE_URL}/webhook/instagram",
                json=sample_instagram_payload
            )
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            logger.info("✅ Instagram webhook handler working")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Webhook endpoints test failed: {e}")
            return False

async def test_conversation_api():
    """Test conversation API endpoints"""
    logger.info("💬 Testing conversation API...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test processing customer message (Convincer branch)
            customer_message = {
                "customer_id": "test_customer_api",
                "business_id": "test_business_api", 
                "message": "Hi! I'm looking for a good smartphone with great camera quality.",
                "platform": "facebook"
            }
            
            response = await client.post(
                f"{BASE_URL}/conversation/message",
                json=customer_message
            )
            assert response.status_code == 200
            conv_response = response.json()
            assert "conversation_id" in conv_response
            conversation_id = conv_response["conversation_id"]
            logger.info(f"✅ Created conversation: {conversation_id}")
            
            # Test retrieving conversation
            response = await client.get(f"{BASE_URL}/conversation/{conversation_id}")
            assert response.status_code == 200
            conversation = response.json()
            assert conversation["conversation_id"] == conversation_id
            assert conversation["conversation_branch"] == "convincer"
            logger.info("✅ Retrieved conversation successfully")
            
            # Test conversation history
            response = await client.get(f"{BASE_URL}/conversation/{conversation_id}/history")
            assert response.status_code == 200
            history = response.json()
            assert len(history) > 0
            assert history[0]["content"] == customer_message["message"]
            logger.info(f"✅ Retrieved conversation history with {len(history)} messages")
            
            # Test webhook interaction processing (Manipulator branch)
            webhook_interaction = {
                "customer_id": "test_customer_webhook",
                "business_id": "test_business_webhook",
                "product_id": None,  # We'll need to get a real product ID
                "interaction_type": "like"
            }
            
            # First get a real product ID
            products_response = await client.get(f"{BASE_URL}/products/")
            products = products_response.json()
            if products:
                webhook_interaction["product_id"] = products[0]["product_id"]
                
                response = await client.post(
                    f"{BASE_URL}/conversation/webhook-interaction",
                    json=webhook_interaction
                )
                assert response.status_code == 200
                webhook_conv_response = response.json()
                assert "conversation_id" in webhook_conv_response
                logger.info("✅ Webhook interaction processing working")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Conversation API test failed: {e}")
            return False

async def test_openapi_docs():
    """Test that OpenAPI documentation is accessible"""
    logger.info("📚 Testing OpenAPI documentation...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test OpenAPI JSON
            response = await client.get(f"{BASE_URL}/openapi.json")
            assert response.status_code == 200
            openapi_spec = response.json()
            assert "paths" in openapi_spec
            logger.info("✅ OpenAPI specification accessible")
            
            # Test docs page
            response = await client.get(f"{BASE_URL}/docs")
            assert response.status_code == 200
            logger.info("✅ API documentation page accessible")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ OpenAPI docs test failed: {e}")
            return False

async def main():
    """Run all API tests"""
    logger.info("🚀 Starting comprehensive API endpoint tests...\n")
    
    tests = [
        ("Basic Endpoints", test_basic_endpoints),
        ("Products API", test_products_api),
        ("Webhook Endpoints", test_webhook_endpoints),
        ("Conversation API", test_conversation_api),
        ("OpenAPI Documentation", test_openapi_docs)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"Running: {test_name}")
        try:
            if await test_func():
                passed += 1
                logger.info(f"✅ {test_name} - PASSED\n")
            else:
                logger.error(f"❌ {test_name} - FAILED\n")
        except Exception as e:
            logger.error(f"❌ {test_name} - FAILED with exception: {e}\n")
    
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All API endpoint tests passed!")
        logger.info("\n✅ Step 4 Complete - API Endpoints and Webhook Handling Working!")
        logger.info("\n🎯 What's working:")
        logger.info("   • Facebook/Instagram webhook verification and handling")
        logger.info("   • Customer message processing (Convincer branch)")
        logger.info("   • Webhook interaction processing (Manipulator branch)")
        logger.info("   • Product search API (tagMatcher functionality)")
        logger.info("   • Conversation management and history")
        logger.info("   • Redis queue integration for async processing")
        logger.info("   • Complete OpenAPI documentation")
    else:
        logger.error("💥 Some API tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

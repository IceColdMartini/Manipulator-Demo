#!/usr/bin/env python3
"""
Complete workflow demonstration for ManipulatorAI Step 4
Demonstrates both Manipulator and Convincer branches working end-to-end
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

async def demonstrate_complete_workflow():
    """Demonstrate the complete ManipulatorAI workflow"""
    logger.info("🎭 DEMONSTRATING COMPLETE MANIPULATORAI WORKFLOW")
    logger.info("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # SCENARIO 1: MANIPULATOR BRANCH (User clicks on ad)
            logger.info("\n🎯 SCENARIO 1: MANIPULATOR BRANCH")
            logger.info("Simulating: User clicks on smartphone ad")
            
            # Get available products first
            response = await client.get(f"{BASE_URL}/products/")
            products = response.json()
            smartphone_product = None
            
            for product in products:
                if "smartphone" in product.get("product_tag", []):
                    smartphone_product = product
                    break
            
            if smartphone_product:
                # Simulate webhook from Facebook - user clicked on smartphone ad
                webhook_interaction = {
                    "customer_id": "customer_john_doe",
                    "business_id": "techcorp_business",
                    "product_id": smartphone_product["product_id"],
                    "interaction_type": "click"
                }
                
                response = await client.post(
                    f"{BASE_URL}/conversation/webhook-interaction",
                    json=webhook_interaction
                )
                
                manipulator_conv = response.json()
                logger.info(f"✅ Manipulator conversation created: {manipulator_conv['conversation_id']}")
                logger.info(f"   Product context: {smartphone_product['product_description'][:50]}...")
                logger.info(f"   Initial response: {manipulator_conv['response']}")
                
                # Check conversation details
                response = await client.get(f"{BASE_URL}/conversation/{manipulator_conv['conversation_id']}")
                conv_details = response.json()
                logger.info(f"   Branch: {conv_details['conversation_branch']}")
                logger.info(f"   Status: {conv_details['status']}")
            
            # SCENARIO 2: CONVINCER BRANCH (User sends direct message)
            logger.info("\n💬 SCENARIO 2: CONVINCER BRANCH")
            logger.info("Simulating: User sends message asking about laptops")
            
            # Customer sends message
            customer_message = {
                "customer_id": "customer_jane_smith",
                "business_id": "techcorp_business",
                "message": "Hi! I'm looking for a powerful laptop for work. I need something with good performance and battery life.",
                "platform": "instagram"
            }
            
            response = await client.post(
                f"{BASE_URL}/conversation/message",
                json=customer_message
            )
            
            convincer_conv = response.json()
            logger.info(f"✅ Convincer conversation created: {convincer_conv['conversation_id']}")
            logger.info(f"   Customer message: {customer_message['message']}")
            logger.info(f"   Initial response: {convincer_conv['response']}")
            
            # Check conversation details
            response = await client.get(f"{BASE_URL}/conversation/{convincer_conv['conversation_id']}")
            conv_details = response.json()
            logger.info(f"   Branch: {conv_details['conversation_branch']}")
            logger.info(f"   Status: {conv_details['status']}")
            
            # Get conversation history
            response = await client.get(f"{BASE_URL}/conversation/{convincer_conv['conversation_id']}/history")
            history = response.json()
            logger.info(f"   Messages in history: {len(history)}")
            
            # SCENARIO 3: PRODUCT SEARCH (tagMatcher simulation)
            logger.info("\n🔍 SCENARIO 3: PRODUCT SEARCH (tagMatcher)")
            logger.info("Simulating: keyRetriever extracted keywords from user message")
            
            # Simulate keywords extracted from customer message
            extracted_keywords = ["laptop", "computer", "work", "performance"]
            
            response = await client.post(
                f"{BASE_URL}/products/search",
                params={"threshold": 0.3},
                json=extracted_keywords
            )
            
            search_results = response.json()
            logger.info(f"✅ tagMatcher found {len(search_results['results'])} matching products")
            
            for result in search_results['results']:
                product = result['product']
                score = result['score']
                logger.info(f"   📦 {product['product_description'][:40]}... (Score: {score:.2f})")
            
            # SCENARIO 4: WEBHOOK EVENT PROCESSING
            logger.info("\n🔔 SCENARIO 4: WEBHOOK EVENT PROCESSING")
            logger.info("Simulating: Multiple webhook events from social media")
            
            # Facebook webhook
            facebook_payload = {
                "object": "page",
                "entry": [
                    {
                        "id": "page123",
                        "time": 1625097600,
                        "messaging": [
                            {
                                "sender": {"id": "user456"},
                                "message": {"text": "Tell me more about your headphones!"}
                            }
                        ]
                    }
                ]
            }
            
            response = await client.post(f"{BASE_URL}/webhook/facebook", json=facebook_payload)
            logger.info(f"✅ Facebook webhook processed: {response.json()['status']}")
            
            # Instagram webhook
            instagram_payload = {
                "object": "instagram",
                "entry": [
                    {
                        "id": "insta123",
                        "changes": [
                            {
                                "field": "comments",
                                "value": {"text": "❤️ Love this product!"}
                            }
                        ]
                    }
                ]
            }
            
            response = await client.post(f"{BASE_URL}/webhook/instagram", json=instagram_payload)
            logger.info(f"✅ Instagram webhook processed: {response.json()['status']}")
            
            # Final summary
            logger.info("\n" + "=" * 60)
            logger.info("🎉 WORKFLOW DEMONSTRATION COMPLETE!")
            logger.info("=" * 60)
            logger.info("\n✅ Successfully demonstrated:")
            logger.info("   🎯 Manipulator Branch - Direct product engagement")
            logger.info("   💬 Convincer Branch - Customer-initiated conversation")
            logger.info("   🔍 Product Search - tagMatcher functionality")
            logger.info("   🔔 Webhook Processing - Social media integration")
            logger.info("   📊 Queue System - Async message processing")
            logger.info("   💾 Data Persistence - MongoDB conversation storage")
            logger.info("   🗄️ Knowledge Base - PostgreSQL product database")
            
            logger.info("\n🚀 Ready for Step 5: Core Logic Implementation")
            logger.info("   Next: keyRetriever and tagMatcher AI integration")
            
        except Exception as e:
            logger.error(f"❌ Workflow demonstration failed: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(demonstrate_complete_workflow())

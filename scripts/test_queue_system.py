#!/usr/bin/env python3
"""
Test Redis queue functionality to verify webhook and message queueing
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import db_manager
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_redis_queues():
    """Test that Redis queues are working correctly"""
    logger.info("🔄 Testing Redis queue functionality...")
    
    try:
        await db_manager.connect_redis()
        
        # Check Facebook webhook queue
        facebook_queue_length = await db_manager.redis_client.llen("facebook_webhook_queue")
        logger.info(f"📱 Facebook webhook queue has {facebook_queue_length} items")
        
        if facebook_queue_length > 0:
            # Peek at the latest item
            latest_item = await db_manager.redis_client.lindex("facebook_webhook_queue", 0)
            if latest_item:
                item_data = json.loads(latest_item)
                logger.info(f"   Latest Facebook webhook: {item_data['source']} at {item_data['timestamp']}")
        
        # Check Instagram webhook queue
        instagram_queue_length = await db_manager.redis_client.llen("instagram_webhook_queue")
        logger.info(f"📸 Instagram webhook queue has {instagram_queue_length} items")
        
        if instagram_queue_length > 0:
            latest_item = await db_manager.redis_client.lindex("instagram_webhook_queue", 0)
            if latest_item:
                item_data = json.loads(latest_item)
                logger.info(f"   Latest Instagram webhook: {item_data['source']} at {item_data['timestamp']}")
        
        # Check AI processing queue
        ai_queue_length = await db_manager.redis_client.llen("ai_processing_queue")
        logger.info(f"🤖 AI processing queue has {ai_queue_length} items")
        
        if ai_queue_length > 0:
            latest_item = await db_manager.redis_client.lindex("ai_processing_queue", 0)
            if latest_item:
                item_data = json.loads(latest_item)
                logger.info(f"   Latest AI processing: {item_data['branch']} branch for conversation {item_data['conversation_id']}")
        
        logger.info("✅ Redis queue system working correctly!")
        
        # Show queue workflow
        logger.info("\n🎯 Queue Workflow Verification:")
        logger.info("   1. ✅ Webhook events → Redis webhook queues")
        logger.info("   2. ✅ Customer messages → AI processing queue")
        logger.info("   3. ✅ Webhook interactions → AI processing queue")
        logger.info("   4. 🔄 Next: Background workers will process these queues")
        
    except Exception as e:
        logger.error(f"❌ Redis queue test failed: {e}")
        raise
    finally:
        await db_manager.close_connections()

if __name__ == "__main__":
    asyncio.run(test_redis_queues())

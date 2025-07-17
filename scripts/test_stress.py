#!/usr/bin/env python3
"""
Database Stress Test - Simulates production load
Tests database performance under concurrent user scenarios
"""

import asyncio
import sys
from pathlib import Path
import time
import random
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import db_manager
from app.services.product_service import ProductService
from app.services.conversation_service import ConversationService
from app.models.schemas import (
    ProductCreate, ConversationCreate, ConversationMessage, 
    MessageSender, ConversationBranch
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StressTester:
    def __init__(self):
        self.results = {
            'products_created': 0,
            'products_read': 0,
            'conversations_created': 0,
            'messages_added': 0,
            'redis_operations': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }

    async def simulate_user_session(self, user_id: int):
        """Simulate a complete user session with database operations"""
        try:
            # 1. User searches for products (PostgreSQL READ)
            async with db_manager.get_postgres_session() as session:
                product_service = ProductService(session)
                
                # Simulate search
                search_terms = ['laptop', 'phone', 'headphones', 'electronics']
                search_term = random.choice(search_terms)
                products = await product_service.search_products_by_keywords([search_term])
                self.results['products_read'] += 1
                
                # Sometimes create a new product (simulate admin adding inventory)
                if user_id % 10 == 0:  # 10% of users are admins adding products
                    product = await product_service.create_product(ProductCreate(
                        name=f"Product from User {user_id}",
                        description=f"Product created by user {user_id} during stress test",
                        price=round(random.uniform(10.0, 1000.0), 2),
                        currency="USD",
                        category=random.choice(['Electronics', 'Audio', 'Computing']),
                        metadata={'user_id': str(user_id), 'stress_test': True}
                    ))
                    self.results['products_created'] += 1

            # 2. Start conversation (MongoDB WRITE)
            mongo_db = db_manager.get_mongo_db()
            conversation_service = ConversationService(mongo_db)
            
            conversation = await conversation_service.create_conversation(ConversationCreate(
                customer_id=f"stress_user_{user_id}",
                business_id=f"business_{user_id % 5}",  # 5 different businesses
                product_context=[str(random.randint(1, 100))],
                conversation_branch=random.choice([ConversationBranch.MANIPULATOR, ConversationBranch.CONVINCER])
            ))
            self.results['conversations_created'] += 1
            
            # 3. Add multiple messages to conversation (MongoDB UPDATE)
            messages = [
                "Hello, I'm interested in your products!",
                "Can you tell me more about the pricing?",
                "Do you have any discounts available?",
                "What's the warranty on this item?",
                "I'd like to proceed with the purchase."
            ]
            
            for i, message_content in enumerate(messages):
                if i >= 3 and random.random() > 0.7:  # Not all users complete full conversation
                    break
                    
                message = ConversationMessage(
                    timestamp=datetime.now(),
                    sender=MessageSender.CUSTOMER,
                    content=message_content,
                    intent=random.choice(['inquiry', 'purchase_intent', 'price_check']),
                    sentiment=random.choice(['positive', 'neutral', 'negative'])
                )
                
                await conversation_service.add_message(conversation.conversation_id, message)
                self.results['messages_added'] += 1
                
                # Simulate some delay between messages
                await asyncio.sleep(random.uniform(0.01, 0.05))

            # 4. Cache user session data (Redis WRITE/READ)
            redis_client = db_manager.get_redis_client()
            
            # Set session data
            session_key = f"user:{user_id}:session"
            session_data = f"active_since_{int(time.time())}"
            await redis_client.setex(session_key, 3600, session_data)  # 1 hour TTL
            
            # Set user preferences
            prefs_key = f"user:{user_id}:preferences"
            prefs_data = f"category:{random.choice(['electronics', 'audio', 'computing'])}"
            await redis_client.set(prefs_key, prefs_data)
            
            # Read session data back
            retrieved_session = await redis_client.get(session_key)
            retrieved_prefs = await redis_client.get(prefs_key)
            
            self.results['redis_operations'] += 3  # 2 writes + 1 read
            
        except Exception as e:
            logger.error(f"Error in user session {user_id}: {e}")
            self.results['errors'] += 1

    async def run_stress_test(self, concurrent_users=50):
        """Run stress test with multiple concurrent users"""
        logger.info(f"🚀 Starting stress test with {concurrent_users} concurrent users...")
        
        # Connect to all databases
        await db_manager.connect_postgresql()
        await db_manager.connect_mongodb()
        await db_manager.connect_redis()
        await db_manager.create_tables()
        
        self.results['start_time'] = time.time()
        
        # Create tasks for concurrent users
        tasks = []
        for user_id in range(concurrent_users):
            task = self.simulate_user_session(user_id)
            tasks.append(task)
        
        # Run all user sessions concurrently
        logger.info("Running concurrent user sessions...")
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.results['end_time'] = time.time()
        
        await db_manager.close_connections()

    def print_performance_report(self):
        """Print detailed performance report"""
        duration = self.results['end_time'] - self.results['start_time']
        
        logger.info("\n" + "="*70)
        logger.info("🏁 DATABASE STRESS TEST PERFORMANCE REPORT")
        logger.info("="*70)
        
        logger.info(f"\n📊 TEST DURATION: {duration:.2f} seconds")
        
        logger.info(f"\n📈 OPERATIONS COMPLETED:")
        logger.info(f"  Products Created: {self.results['products_created']}")
        logger.info(f"  Products Read: {self.results['products_read']}")
        logger.info(f"  Conversations Created: {self.results['conversations_created']}")
        logger.info(f"  Messages Added: {self.results['messages_added']}")
        logger.info(f"  Redis Operations: {self.results['redis_operations']}")
        logger.info(f"  Total Operations: {sum([
            self.results['products_created'],
            self.results['products_read'],
            self.results['conversations_created'],
            self.results['messages_added'],
            self.results['redis_operations']
        ])}")
        
        logger.info(f"\n⚡ PERFORMANCE METRICS:")
        total_ops = sum([
            self.results['products_created'],
            self.results['products_read'],
            self.results['conversations_created'],
            self.results['messages_added'],
            self.results['redis_operations']
        ])
        ops_per_second = total_ops / duration if duration > 0 else 0
        logger.info(f"  Operations per second: {ops_per_second:.2f}")
        logger.info(f"  Average time per operation: {(duration/total_ops)*1000:.2f}ms")
        
        logger.info(f"\n❌ ERRORS:")
        logger.info(f"  Total Errors: {self.results['errors']}")
        error_rate = (self.results['errors'] / total_ops) * 100 if total_ops > 0 else 0
        logger.info(f"  Error Rate: {error_rate:.2f}%")
        
        # Performance assessment
        if error_rate == 0:
            status = "🎉 EXCELLENT"
        elif error_rate < 1:
            status = "✅ GOOD"
        elif error_rate < 5:
            status = "⚠️ ACCEPTABLE"
        else:
            status = "❌ NEEDS IMPROVEMENT"
            
        logger.info(f"\n🏆 OVERALL PERFORMANCE: {status}")
        
        if ops_per_second > 100:
            logger.info("💪 High throughput - Ready for production traffic")
        elif ops_per_second > 50:
            logger.info("👍 Good throughput - Suitable for moderate traffic")
        else:
            logger.info("⚠️ Consider optimization for high-traffic scenarios")

async def main():
    """Run the stress test"""
    tester = StressTester()
    
    try:
        # Test with different user loads
        for user_count in [10, 25, 50]:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing with {user_count} concurrent users")
            logger.info(f"{'='*50}")
            
            await tester.run_stress_test(user_count)
            tester.print_performance_report()
            
            # Reset results for next test
            tester.results = {key: 0 for key in tester.results}
            
            # Brief pause between tests
            await asyncio.sleep(2)
            
    except Exception as e:
        logger.error(f"Stress test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

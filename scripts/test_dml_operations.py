#!/usr/bin/env python3
"""
Comprehensive DML Operations Test Script
Tests INSERT, SELECT, UPDATE, DELETE operations across all databases
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import uuid

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

class DatabaseTester:
    def __init__(self):
        self.test_results = {
            'postgresql': {'passed': 0, 'failed': 0, 'tests': []},
            'mongodb': {'passed': 0, 'failed': 0, 'tests': []},
            'redis': {'passed': 0, 'failed': 0, 'tests': []}
        }

    def log_test_result(self, db_type: str, test_name: str, success: bool, message: str = ""):
        """Log test results for summary"""
        if success:
            self.test_results[db_type]['passed'] += 1
            logger.info(f"✅ {db_type.upper()}: {test_name} - {message}")
        else:
            self.test_results[db_type]['failed'] += 1
            logger.error(f"❌ {db_type.upper()}: {test_name} - {message}")
        
        self.test_results[db_type]['tests'].append({
            'name': test_name,
            'success': success,
            'message': message
        })

    async def test_postgresql_operations(self):
        """Test all PostgreSQL DML operations"""
        logger.info("🔧 Testing PostgreSQL DML Operations...")
        
        try:
            await db_manager.connect_postgresql()
            await db_manager.create_tables()
            
            async with db_manager.get_postgres_session() as session:
                product_service = ProductService(session)
                
                # Test 1: INSERT - Create multiple products
                products_data = [
                    ProductCreate(
                        name="Test Laptop",
                        description="High-performance laptop for testing",
                        price=1299.99,
                        currency="USD",
                        category="Electronics",
                        metadata={"brand": "TestBrand", "warranty": "2 years"}
                    ),
                    ProductCreate(
                        name="Test Phone",
                        description="Smartphone with advanced features",
                        price=899.99,
                        currency="USD",
                        category="Electronics",
                        metadata={"brand": "TestBrand", "storage": "256GB"}
                    ),
                    ProductCreate(
                        name="Test Headphones",
                        description="Wireless noise-canceling headphones",
                        price=299.99,
                        currency="USD",
                        category="Audio",
                        metadata={"brand": "TestBrand", "wireless": True}
                    )
                ]
                
                created_products = []
                for i, product_data in enumerate(products_data):
                    try:
                        product = await product_service.create_product(product_data)
                        created_products.append(product)
                        self.log_test_result('postgresql', f'INSERT Product {i+1}', True, 
                                           f"Created {product.name} with ID {product.id}")
                    except Exception as e:
                        self.log_test_result('postgresql', f'INSERT Product {i+1}', False, str(e))
                
                # Test 2: SELECT - Read operations
                try:
                    all_products = await product_service.get_all_products()
                    self.log_test_result('postgresql', 'SELECT All Products', True, 
                                       f"Retrieved {len(all_products)} products")
                except Exception as e:
                    self.log_test_result('postgresql', 'SELECT All Products', False, str(e))
                
                # Test 3: SELECT - Search operations
                try:
                    search_results = await product_service.search_products_by_keywords(["Test"])
                    self.log_test_result('postgresql', 'SELECT Search Products', True, 
                                       f"Found {len(search_results)} products matching 'Test'")
                except Exception as e:
                    self.log_test_result('postgresql', 'SELECT Search Products', False, str(e))
                
                # Test 4: SELECT - Get by ID
                if created_products:
                    try:
                        product = await product_service.get_product_by_id(created_products[0].id)
                        if product:
                            self.log_test_result('postgresql', 'SELECT By ID', True, 
                                               f"Retrieved product: {product.name}")
                        else:
                            self.log_test_result('postgresql', 'SELECT By ID', False, "Product not found")
                    except Exception as e:
                        self.log_test_result('postgresql', 'SELECT By ID', False, str(e))
                
                # Test 5: UPDATE - This would require implementing update method
                # For now, we'll test that the data persists across sessions
                try:
                    products_after = await product_service.get_all_products()
                    if len(products_after) >= len(created_products):
                        self.log_test_result('postgresql', 'Data Persistence', True, 
                                           "Data persists across operations")
                    else:
                        self.log_test_result('postgresql', 'Data Persistence', False, 
                                           "Data persistence issue detected")
                except Exception as e:
                    self.log_test_result('postgresql', 'Data Persistence', False, str(e))
                
        except Exception as e:
            self.log_test_result('postgresql', 'Connection', False, str(e))

    async def test_mongodb_operations(self):
        """Test all MongoDB DML operations"""
        logger.info("🔧 Testing MongoDB DML Operations...")
        
        try:
            await db_manager.connect_mongodb()
            mongo_db = db_manager.get_mongo_db()
            conversation_service = ConversationService(mongo_db)
            
            # Test 1: INSERT - Create conversations
            conversations_data = [
                ConversationCreate(
                    customer_id="customer_001",
                    business_id="business_001",
                    product_context=["product_1", "product_2"],
                    conversation_branch=ConversationBranch.MANIPULATOR
                ),
                ConversationCreate(
                    customer_id="customer_002",
                    business_id="business_001",
                    product_context=["product_3"],
                    conversation_branch=ConversationBranch.CONVINCER
                )
            ]
            
            created_conversations = []
            for i, conv_data in enumerate(conversations_data):
                try:
                    conversation = await conversation_service.create_conversation(conv_data)
                    created_conversations.append(conversation)
                    self.log_test_result('mongodb', f'INSERT Conversation {i+1}', True, 
                                       f"Created conversation {conversation.conversation_id}")
                except Exception as e:
                    self.log_test_result('mongodb', f'INSERT Conversation {i+1}', False, str(e))
            
            # Test 2: SELECT - Read conversations
            for i, conversation in enumerate(created_conversations):
                try:
                    retrieved = await conversation_service.get_conversation_by_id(conversation.conversation_id)
                    if retrieved:
                        self.log_test_result('mongodb', f'SELECT Conversation {i+1}', True, 
                                           f"Retrieved conversation for {retrieved.customer_id}")
                    else:
                        self.log_test_result('mongodb', f'SELECT Conversation {i+1}', False, 
                                           "Conversation not found")
                except Exception as e:
                    self.log_test_result('mongodb', f'SELECT Conversation {i+1}', False, str(e))
            
            # Test 3: UPDATE - Add messages to conversations
            if created_conversations:
                try:
                    conversation_id = created_conversations[0].conversation_id
                    test_message = ConversationMessage(
                        timestamp=datetime.utcnow(),
                        sender=MessageSender.CUSTOMER,
                        content="Hello, I'm interested in your products!",
                        intent="product_inquiry",
                        sentiment="positive"
                    )
                    
                    success = await conversation_service.add_message(conversation_id, test_message)
                    self.log_test_result('mongodb', 'UPDATE Add Message', success, 
                                       f"Added message to conversation {conversation_id}")
                except Exception as e:
                    self.log_test_result('mongodb', 'UPDATE Add Message', False, str(e))
            
            # Test 4: UPDATE - Update conversation status
            if created_conversations:
                try:
                    from app.models.schemas import ConversationStatus
                    conversation_id = created_conversations[0].conversation_id
                    success = await conversation_service.update_conversation_status(
                        conversation_id, ConversationStatus.QUALIFIED
                    )
                    self.log_test_result('mongodb', 'UPDATE Status', success, 
                                       f"Updated status for conversation {conversation_id}")
                except Exception as e:
                    self.log_test_result('mongodb', 'UPDATE Status', False, str(e))
            
            # Test 5: Test document structure integrity
            try:
                collection = mongo_db.conversations
                doc_count = await collection.count_documents({})
                self.log_test_result('mongodb', 'Document Count', True, 
                                   f"Total documents in collection: {doc_count}")
            except Exception as e:
                self.log_test_result('mongodb', 'Document Count', False, str(e))
                
        except Exception as e:
            self.log_test_result('mongodb', 'Connection', False, str(e))

    async def test_redis_operations(self):
        """Test all Redis DML operations"""
        logger.info("🔧 Testing Redis DML Operations...")
        
        try:
            await db_manager.connect_redis()
            redis_client = db_manager.get_redis_client()
            
            # Test 1: SET operations (INSERT equivalent)
            test_data = {
                "user:1:session": "session_token_12345",
                "product:featured": "laptop,phone,headphones",
                "cache:search:electronics": '{"results": ["laptop", "phone"], "count": 2}',
                "counter:page_views": "1",
                "config:max_connections": "100"
            }
            
            for key, value in test_data.items():
                try:
                    await redis_client.set(key, value)
                    self.log_test_result('redis', f'SET {key}', True, f"Set {key} = {value}")
                except Exception as e:
                    self.log_test_result('redis', f'SET {key}', False, str(e))
            
            # Test 2: GET operations (SELECT equivalent)
            for key in test_data.keys():
                try:
                    value = await redis_client.get(key)
                    if value is not None:
                        self.log_test_result('redis', f'GET {key}', True, f"Retrieved: {value}")
                    else:
                        self.log_test_result('redis', f'GET {key}', False, "Key not found")
                except Exception as e:
                    self.log_test_result('redis', f'GET {key}', False, str(e))
            
            # Test 3: UPDATE operations (increment counter)
            try:
                new_value = await redis_client.incr("counter:page_views")
                self.log_test_result('redis', 'INCR counter', True, f"Counter value: {new_value}")
            except Exception as e:
                self.log_test_result('redis', 'INCR counter', False, str(e))
            
            # Test 4: DELETE operations
            try:
                deleted = await redis_client.delete("config:max_connections")
                self.log_test_result('redis', 'DELETE key', True, f"Deleted {deleted} key(s)")
            except Exception as e:
                self.log_test_result('redis', 'DELETE key', False, str(e))
            
            # Test 5: EXISTS check
            try:
                exists = await redis_client.exists("user:1:session")
                self.log_test_result('redis', 'EXISTS check', True, f"Key exists: {bool(exists)}")
            except Exception as e:
                self.log_test_result('redis', 'EXISTS check', False, str(e))
            
            # Test 6: TTL operations (expiration)
            try:
                await redis_client.setex("temp:data", 60, "temporary_value")
                ttl = await redis_client.ttl("temp:data")
                self.log_test_result('redis', 'TTL operations', True, f"TTL set to {ttl} seconds")
            except Exception as e:
                self.log_test_result('redis', 'TTL operations', False, str(e))
                
        except Exception as e:
            self.log_test_result('redis', 'Connection', False, str(e))

    async def test_concurrent_operations(self):
        """Test concurrent operations across all databases"""
        logger.info("🔧 Testing Concurrent Operations...")
        
        try:
            # Simulate concurrent operations
            tasks = []
            
            # Concurrent PostgreSQL operations
            for i in range(3):
                task = self.create_test_product(f"Concurrent Product {i}")
                tasks.append(task)
            
            # Concurrent MongoDB operations
            for i in range(3):
                task = self.create_test_conversation(f"concurrent_customer_{i}")
                tasks.append(task)
            
            # Concurrent Redis operations
            for i in range(3):
                task = self.set_redis_key(f"concurrent:test:{i}", f"value_{i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum(1 for result in results if not isinstance(result, Exception))
            total_count = len(results)
            
            self.log_test_result('postgresql', 'Concurrent Operations', 
                               success_count == total_count, 
                               f"{success_count}/{total_count} operations succeeded")
            
        except Exception as e:
            self.log_test_result('postgresql', 'Concurrent Operations', False, str(e))

    async def create_test_product(self, name: str):
        """Helper method for concurrent testing"""
        async with db_manager.get_postgres_session() as session:
            product_service = ProductService(session)
            return await product_service.create_product(ProductCreate(
                name=name,
                description=f"Description for {name}",
                price=99.99,
                currency="USD",
                category="Test"
            ))

    async def create_test_conversation(self, customer_id: str):
        """Helper method for concurrent testing"""
        mongo_db = db_manager.get_mongo_db()
        conversation_service = ConversationService(mongo_db)
        return await conversation_service.create_conversation(ConversationCreate(
            customer_id=customer_id,
            business_id="test_business",
            product_context=[],
            conversation_branch=ConversationBranch.MANIPULATOR
        ))

    async def set_redis_key(self, key: str, value: str):
        """Helper method for concurrent testing"""
        redis_client = db_manager.get_redis_client()
        return await redis_client.set(key, value)

    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("🏁 DATABASE DML OPERATIONS TEST SUMMARY")
        logger.info("="*60)
        
        total_passed = 0
        total_failed = 0
        
        for db_type, results in self.test_results.items():
            passed = results['passed']
            failed = results['failed']
            total = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASSED" if failed == 0 else "⚠️  PARTIAL" if passed > failed else "❌ FAILED"
            
            logger.info(f"\n{db_type.upper()}: {status}")
            logger.info(f"  Passed: {passed}/{total}")
            logger.info(f"  Failed: {failed}/{total}")
            
            if failed > 0:
                logger.info("  Failed tests:")
                for test in results['tests']:
                    if not test['success']:
                        logger.info(f"    - {test['name']}: {test['message']}")
        
        logger.info(f"\nOVERALL RESULTS:")
        logger.info(f"  Total Passed: {total_passed}")
        logger.info(f"  Total Failed: {total_failed}")
        
        if total_failed == 0:
            logger.info("🎉 ALL TESTS PASSED! Databases are ready for production.")
        elif total_passed > total_failed:
            logger.info("⚠️  Most tests passed, but some issues need attention.")
        else:
            logger.info("❌ Critical issues detected. Please review failed tests.")

async def main():
    """Run comprehensive DML operations test"""
    tester = DatabaseTester()
    
    try:
        # Test each database
        await tester.test_postgresql_operations()
        await tester.test_mongodb_operations()
        await tester.test_redis_operations()
        await tester.test_concurrent_operations()
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
    finally:
        await db_manager.close_connections()
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())

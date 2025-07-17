#!/usr/bin/env python3
"""
Comprehensive FastAPI Application Test
Tests all endpoints and functionality of the main FastAPI application
"""

import asyncio
import httpx
import sys
import time
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8004"

class FastAPITester:
    """Comprehensive tester for the main FastAPI application"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        if success:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
    
    async def test_root_endpoint(self):
        """Test the root endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    has_message = "message" in data
                    has_version = "version" in data
                    has_endpoints = "endpoints" in data
                    success = has_message and has_version and has_endpoints
                    details = f"Status: {response.status_code}, Message: {'✅' if has_message else '❌'}, Endpoints: {'✅' if has_endpoints else '❌'}"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("Root Endpoint", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Root Endpoint", False, f"Error: {e}")
            return False
    
    async def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/health")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    status_healthy = data.get("status") == "healthy"
                    has_databases = "databases" in data
                    success = status_healthy and has_databases
                    
                    if has_databases:
                        db_status = data["databases"]
                        pg_status = db_status.get("postgresql", "unknown")
                        mongo_status = db_status.get("mongodb", "unknown")
                        redis_status = db_status.get("redis", "unknown")
                        details = f"Status: {response.status_code}, PG: {pg_status}, Mongo: {mongo_status}, Redis: {redis_status}"
                    else:
                        details = f"Status: {response.status_code}, No database info"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("Health Check", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Health Check", False, f"Error: {e}")
            return False
    
    async def test_ai_keyword_extraction(self):
        """Test AI keyword extraction endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "message": "I'm looking for a gaming laptop with great graphics card",
                    "business_context": "We sell high-performance laptops and gaming computers"
                }
                
                response = await client.post(
                    f"{BASE_URL}/ai/extract-keywords",
                    json=payload,
                    timeout=30.0
                )
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    keywords = data.get("extracted_keywords", [])
                    success = len(keywords) > 0 and data.get("subsystem") == "keyRetriever"
                    details = f"Status: {response.status_code}, Keywords: {keywords}"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("AI Keyword Extraction", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("AI Keyword Extraction", False, f"Error: {e}")
            return False
    
    async def test_ai_product_matching(self):
        """Test AI product matching endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "keywords": ["laptop", "gaming", "graphics"],
                    "threshold": 0.3
                }
                
                response = await client.post(
                    f"{BASE_URL}/ai/match-products",
                    json=payload,
                    timeout=30.0
                )
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    matches = data.get("matches", [])
                    subsystem = data.get("subsystem", "")
                    success = subsystem == "tagMatcher"
                    details = f"Status: {response.status_code}, Matches: {len(matches)}, Subsystem: {subsystem}"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("AI Product Matching", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("AI Product Matching", False, f"Error: {e}")
            return False
    
    async def test_ai_full_pipeline(self):
        """Test the full AI pipeline"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "message": "Hi! I need a smartphone with excellent camera for photography",
                    "business_context": "We sell premium smartphones and mobile accessories"
                }
                
                response = await client.post(
                    f"{BASE_URL}/ai/full-pipeline",
                    json=payload,
                    timeout=45.0
                )
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    pipeline_status = data.get("pipeline_status", "")
                    keywords = data.get("step_1_keywords", [])
                    matches = data.get("step_2_matches", 0)
                    ai_response = data.get("step_3_ai_response", "")
                    
                    success = (
                        pipeline_status == "complete" and 
                        len(keywords) > 0 and 
                        len(ai_response) > 20
                    )
                    details = f"Status: {response.status_code}, Pipeline: {pipeline_status}, Keywords: {len(keywords)}, Matches: {matches}, Response: {len(ai_response)} chars"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("AI Full Pipeline", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("AI Full Pipeline", False, f"Error: {e}")
            return False
    
    async def test_products_endpoints(self):
        """Test products API endpoints"""
        try:
            async with httpx.AsyncClient() as client:
                # Test get all products
                response = await client.get(f"{BASE_URL}/products/")
                success = response.status_code == 200
                
                if success:
                    products = response.json()
                    products_count = len(products) if isinstance(products, list) else 0
                    details = f"Status: {response.status_code}, Products count: {products_count}"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("Products API", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Products API", False, f"Error: {e}")
            return False
    
    async def test_conversations_endpoint(self):
        """Test conversations API endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "customer_id": "test_customer_comprehensive",
                    "business_id": "test_business_comprehensive",
                    "message": "Hi! I'm interested in your products",
                    "platform": "facebook"
                }
                
                response = await client.post(
                    f"{BASE_URL}/conversation/message",
                    json=payload,
                    timeout=30.0
                )
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    has_conversation_id = "conversation_id" in data
                    has_response = "response" in data or "ai_response" in data
                    success = has_conversation_id
                    details = f"Status: {response.status_code}, Conv ID: {'✅' if has_conversation_id else '❌'}, Response: {'✅' if has_response else '❌'}"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("Conversations API", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Conversations API", False, f"Error: {e}")
            return False
    
    async def test_webhooks_endpoint(self):
        """Test webhooks endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                # Test webhook verification (GET request)
                params = {
                    "hub.mode": "subscribe",
                    "hub.verify_token": "test_facebook_verify_token",
                    "hub.challenge": "test_challenge_123"
                }
                
                response = await client.get(f"{BASE_URL}/webhook/facebook", params=params)
                success = response.status_code == 200
                
                if success:
                    challenge_response = response.text.strip('"')  # Remove quotes if present
                    success = challenge_response == "test_challenge_123"
                    details = f"Status: {response.status_code}, Challenge verified: {'✅' if success else '❌'}"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("Webhooks API", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Webhooks API", False, f"Error: {e}")
            return False
    
    async def test_api_documentation(self):
        """Test API documentation endpoints"""
        try:
            async with httpx.AsyncClient() as client:
                # Test OpenAPI docs
                response = await client.get(f"{BASE_URL}/docs")
                docs_success = response.status_code == 200
                
                # Test OpenAPI JSON
                response = await client.get(f"{BASE_URL}/openapi.json")
                openapi_success = response.status_code == 200
                
                success = docs_success and openapi_success
                details = f"Docs: {'✅' if docs_success else '❌'}, OpenAPI: {'✅' if openapi_success else '❌'}"
                
                self.log_test_result("API Documentation", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("API Documentation", False, f"Error: {e}")
            return False
    
    async def test_performance_metrics(self):
        """Test application performance under load"""
        try:
            async with httpx.AsyncClient() as client:
                start_time = time.time()
                
                # Create multiple concurrent requests
                tasks = []
                for i in range(5):
                    task = client.get(f"{BASE_URL}/health")
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                total_time = time.time() - start_time
                
                successful_requests = sum(
                    1 for r in responses 
                    if isinstance(r, httpx.Response) and r.status_code == 200
                )
                
                success = successful_requests >= 4 and total_time < 5
                details = f"5 requests in {total_time:.2f}s, {successful_requests}/5 successful, {successful_requests/total_time:.1f} req/sec"
                
                self.log_test_result("Performance Metrics", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Performance Metrics", False, f"Error: {e}")
            return False
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🧪 FASTAPI APPLICATION COMPREHENSIVE TESTING")
        print("="*55)
        
        print("\n📋 Basic Application Tests:")
        await self.test_root_endpoint()
        await self.test_health_endpoint()
        await self.test_api_documentation()
        
        print("\n🧠 AI Integration Tests:")
        await self.test_ai_keyword_extraction()
        await self.test_ai_product_matching()
        await self.test_ai_full_pipeline()
        
        print("\n🛍️ Business Logic Tests:")
        await self.test_products_endpoints()
        await self.test_conversations_endpoint()
        await self.test_webhooks_endpoint()
        
        print("\n⚡ Performance Tests:")
        await self.test_performance_metrics()
        
        # Summary
        print("\n" + "="*55)
        print("📊 COMPREHENSIVE TEST SUMMARY:")
        print(f"   ✅ Tests Passed: {self.tests_passed}")
        print(f"   ❌ Tests Failed: {self.tests_failed}")
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ FastAPI Application: FULLY OPERATIONAL")
            print("✅ Azure OpenAI Integration: WORKING")
            print("✅ Database Connections: ESTABLISHED")
            print("✅ All API Endpoints: FUNCTIONAL")
            return True
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed.")
            print("🔧 Some functionality may need attention.")
            return False

async def main():
    """Main test runner"""
    try:
        print("🚀 Starting comprehensive FastAPI application tests...")
        print("📡 Testing application at: http://127.0.0.1:8004")
        
        # Wait a moment for the application to be ready
        await asyncio.sleep(2)
        
        tester = FastAPITester()
        success = await tester.run_comprehensive_tests()
        
        if success:
            print("\n🚀 FASTAPI APPLICATION: FULLY OPERATIONAL!")
            print("All endpoints working perfectly with Azure OpenAI integration.")
        else:
            print("\n🔧 Some tests failed. Check the results above.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n🏁 Test completed with {'success' if result else 'some failures'}")
    sys.exit(0 if result else 1)

#!/usr/bin/env python3
"""
Simplified API Endpoint Test for Azure OpenAI Integration
Tests Azure OpenAI through simplified FastAPI endpoints
"""

import asyncio
import httpx
import sys
import time
import subprocess
import signal
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8003"

class SimplifiedAPITester:
    """Test Azure OpenAI integration through simplified API endpoints"""
    
    def __init__(self):
        self.app_process = None
        self.tests_passed = 0
        self.tests_failed = 0
    
    def start_application(self):
        """Start the simplified FastAPI application"""
        try:
            print("🚀 Starting simplified FastAPI application...")
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app.main_simple:app", 
                "--host", "127.0.0.1", 
                "--port", "8003",
                "--reload"
            ]
            
            self.app_process = subprocess.Popen(
                cmd, 
                cwd=Path(__file__).parent.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for app to start
            print("⏳ Waiting for application to start...")
            time.sleep(10)  # Give it time to start
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start application: {e}")
            return False
    
    def stop_application(self):
        """Stop the FastAPI application"""
        if self.app_process:
            print("🛑 Stopping application...")
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.app_process.kill()
                self.app_process.wait()
    
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
    
    async def test_health_check(self):
        """Test basic application health"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/health")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    azure_configured = data.get("azure_openai_configured", False)
                    details = f"Status: {response.status_code}, Azure OpenAI: {'✅' if azure_configured else '❌'}"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("Application Health Check", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Application Health Check", False, f"Error: {e}")
            return False
    
    async def test_ai_health_check(self):
        """Test AI service health"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/api/v1/ai/health")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    ai_status = data.get("status", "unknown")
                    azure_status = data.get("azure_openai", "unknown")
                    details = f"AI: {ai_status}, Azure: {azure_status}"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("AI Service Health Check", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("AI Service Health Check", False, f"Error: {e}")
            return False
    
    async def test_keyword_extraction_endpoint(self):
        """Test keyword extraction through API"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "message": "I'm looking for a smartphone with great camera quality",
                    "business_context": "We sell electronics including smartphones and accessories"
                }
                
                response = await client.post(
                    f"{BASE_URL}/api/v1/ai/extract-keywords",
                    json=payload,
                    timeout=30.0
                )
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    keywords = data.get("extracted_keywords", [])
                    success = len(keywords) > 0 and data.get("status") == "success"
                    details = f"Status: {response.status_code}, Keywords: {keywords}"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("Keyword Extraction API", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Keyword Extraction API", False, f"Error: {e}")
            return False
    
    async def test_response_generation_endpoint(self):
        """Test response generation through API"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "message": "Hi! I need a laptop for gaming and programming",
                    "branch": "convincer",
                    "is_welcome": True
                }
                
                response = await client.post(
                    f"{BASE_URL}/api/v1/ai/generate-response",
                    json=payload,
                    timeout=30.0
                )
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    ai_response = data.get("ai_response", "")
                    success = len(ai_response) > 20 and data.get("status") == "success"
                    details = f"Status: {response.status_code}, Response length: {len(ai_response)}"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("Response Generation API", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Response Generation API", False, f"Error: {e}")
            return False
    
    async def test_full_pipeline_endpoint(self):
        """Test full AI pipeline through API"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "message": "Hi! I need a laptop for gaming and programming",
                    "business_context": "We sell high-performance laptops and gaming computers",
                    "branch": "convincer"
                }
                
                response = await client.post(
                    f"{BASE_URL}/api/v1/ai/full-pipeline",
                    json=payload,
                    timeout=45.0
                )
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    pipeline_status = data.get("pipeline_status", "")
                    ai_response = data.get("step_3_ai_response", "")
                    keywords = data.get("step_1_keywords", [])
                    matches = data.get("step_2_matches", 0)
                    
                    success = (
                        pipeline_status == "complete" and 
                        len(ai_response) > 20 and 
                        len(keywords) > 0 and 
                        data.get("status") == "success"
                    )
                    details = f"Pipeline: {pipeline_status}, Keywords: {len(keywords)}, Matches: {matches}, Response: {len(ai_response)} chars"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test_result("Full AI Pipeline API", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Full AI Pipeline API", False, f"Error: {e}")
            return False
    
    async def test_docs_accessibility(self):
        """Test API documentation accessibility"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/docs")
                success = response.status_code == 200
                
                self.log_test_result("API Documentation", success, f"Status: {response.status_code}")
                return success
                
        except Exception as e:
            self.log_test_result("API Documentation", False, f"Error: {e}")
            return False
    
    async def test_performance_under_load(self):
        """Test API performance with multiple requests"""
        try:
            async with httpx.AsyncClient() as client:
                start_time = time.time()
                
                # Create 3 concurrent requests
                tasks = []
                for i in range(3):
                    payload = {
                        "message": f"I need a smartphone {i}",
                        "business_context": "We sell mobile devices"
                    }
                    task = client.post(
                        f"{BASE_URL}/api/v1/ai/extract-keywords",
                        json=payload,
                        timeout=30.0
                    )
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                total_time = time.time() - start_time
                
                successful_requests = sum(
                    1 for r in responses 
                    if isinstance(r, httpx.Response) and r.status_code == 200
                )
                
                success = successful_requests >= 2 and total_time < 20
                details = f"3 requests in {total_time:.2f}s, {successful_requests}/3 successful"
                
                self.log_test_result("Performance Under Load", success, details)
                return success
                
        except Exception as e:
            self.log_test_result("Performance Under Load", False, f"Error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all API tests"""
        print("🧪 AZURE OPENAI SIMPLIFIED API TESTING")
        print("="*50)
        
        # Start application
        if not self.start_application():
            print("❌ Failed to start application. Cannot proceed with tests.")
            return False
        
        try:
            print("\n📋 Basic Tests:")
            await self.test_health_check()
            await self.test_ai_health_check()
            await self.test_docs_accessibility()
            
            print("\n🧠 AI Integration Tests:")
            await self.test_keyword_extraction_endpoint()
            await self.test_response_generation_endpoint()
            await self.test_full_pipeline_endpoint()
            
            print("\n⚡ Performance Tests:")
            await self.test_performance_under_load()
            
            # Summary
            print("\n" + "="*50)
            print("📊 SIMPLIFIED API TEST SUMMARY:")
            print(f"   ✅ Tests Passed: {self.tests_passed}")
            print(f"   ❌ Tests Failed: {self.tests_failed}")
            
            if self.tests_failed == 0:
                print("\n🎉 ALL API TESTS PASSED!")
                print("✅ Azure OpenAI integration through FastAPI: WORKING")
                return True
            else:
                print(f"\n⚠️  {self.tests_failed} test(s) failed.")
                return False
        
        finally:
            self.stop_application()

async def main():
    """Main test runner"""
    try:
        tester = SimplifiedAPITester()
        success = await tester.run_all_tests()
        
        if success:
            print("\n🚀 AZURE OPENAI FASTAPI INTEGRATION: FULLY OPERATIONAL!")
            print("✅ Simplified FastAPI application with Azure OpenAI working perfectly")
        else:
            print("\n🔧 Some API tests failed. Check the logs above.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)

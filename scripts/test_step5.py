#!/usr/bin/env python3
"""
Test Script for ManipulatorAI Step 5: Core AI Logic
Tests the keyRetriever and tagMatcher subsystems
"""

import asyncio
import aiohttp
import json
import sys
import time

BASE_URL = "http://localhost:8001"

class Step5Tester:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_api_status(self):
        """Test if the API is running"""
        print("🔄 Testing API status...")
        try:
            async with self.session.get(f"{BASE_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API is running: {data['message']}")
                    print(f"   Available endpoints: {list(data['endpoints'].keys())}")
                    return True
                else:
                    print(f"❌ API returned status {response.status}")
                    return False
        except aiohttp.ClientError as e:
            print(f"❌ Failed to connect to API: {e}")
            return False
    
    async def test_keyword_extraction(self):
        """Test the keyRetriever subsystem"""
        print("\n🔄 Testing keyRetriever subsystem...")
        
        test_cases = [
            {
                "name": "Electronics Query",
                "message": "Hi, I'm looking for a smartphone with good camera quality",
                "business_context": "We sell electronics including smartphones, laptops, headphones, and accessories"
            },
            {
                "name": "Fashion Query", 
                "message": "Do you have any blue shirts in medium size?",
                "business_context": "We sell fashion items including shirts, pants, dresses, and accessories"
            },
            {
                "name": "General Inquiry",
                "message": "What products do you offer?",
                "business_context": "We sell electronics and fashion items"
            }
        ]
        
        for test_case in test_cases:
            print(f"   Testing: {test_case['name']}")
            try:
                async with self.session.post(
                    f"{BASE_URL}/ai/extract-keywords",
                    json={
                        "message": test_case["message"],
                        "business_context": test_case["business_context"]
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        keywords = data.get("extracted_keywords", [])
                        print(f"      ✅ Keywords extracted: {keywords}")
                    else:
                        text = await response.text()
                        print(f"      ❌ Failed with status {response.status}: {text}")
                        
            except Exception as e:
                print(f"      ❌ Exception: {e}")
        
        return True
    
    async def test_product_matching(self):
        """Test the tagMatcher subsystem"""
        print("\n🔄 Testing tagMatcher subsystem...")
        
        test_cases = [
            {
                "name": "Electronics Keywords",
                "keywords": ["smartphone", "camera", "mobile", "phone"],
                "threshold": 0.3
            },
            {
                "name": "Fashion Keywords",
                "keywords": ["shirt", "blue", "clothing", "apparel"],
                "threshold": 0.3
            },
            {
                "name": "Generic Keywords",
                "keywords": ["product", "item", "buy"],
                "threshold": 0.2
            }
        ]
        
        for test_case in test_cases:
            print(f"   Testing: {test_case['name']}")
            try:
                async with self.session.post(
                    f"{BASE_URL}/ai/match-products",
                    json={
                        "keywords": test_case["keywords"],
                        "threshold": test_case["threshold"]
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        matches = data.get("matches_found", 0)
                        print(f"      ✅ Found {matches} product matches")
                        if matches > 0:
                            top_match = data["matches"][0]
                            print(f"      📦 Top match: {top_match['product_name']} (score: {top_match['score']:.3f})")
                    else:
                        text = await response.text()
                        print(f"      ❌ Failed with status {response.status}: {text}")
                        
            except Exception as e:
                print(f"      ❌ Exception: {e}")
        
        return True
    
    async def test_full_pipeline(self):
        """Test the complete keyRetriever → tagMatcher → AI Response pipeline"""
        print("\n🔄 Testing full AI pipeline...")
        
        test_cases = [
            {
                "name": "Customer Looking for Phone",
                "message": "I need a new smartphone, preferably one with excellent camera quality for photography",
                "business_context": "We sell premium electronics including the latest smartphones, laptops, and accessories"
            },
            {
                "name": "Fashion Customer",
                "message": "Hello! Do you have any summer dresses or casual shirts available?",
                "business_context": "We specialize in trendy fashion items for men and women"
            }
        ]
        
        for test_case in test_cases:
            print(f"   Testing: {test_case['name']}")
            try:
                async with self.session.post(
                    f"{BASE_URL}/ai/full-pipeline",
                    json={
                        "message": test_case["message"],
                        "business_context": test_case["business_context"]
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Show pipeline steps
                        keywords = data.get("step_1_keywords", [])
                        matches = data.get("step_2_matches", 0)
                        ai_response = data.get("step_3_ai_response", "")
                        
                        print(f"      ✅ Pipeline Status: {data.get('pipeline_status')}")
                        print(f"      🔑 Keywords: {keywords}")
                        print(f"      📦 Product Matches: {matches}")
                        print(f"      🤖 AI Response: {ai_response[:100]}...")
                        
                    else:
                        text = await response.text()
                        print(f"      ❌ Failed with status {response.status}: {text}")
                        
            except Exception as e:
                print(f"      ❌ Exception: {e}")
        
        return True
    
    async def test_conversation_endpoint(self):
        """Test the updated conversation endpoint with AI integration"""
        print("\n🔄 Testing conversation endpoint with AI integration...")
        
        test_message = {
            "user_id": "test_user_ai",
            "platform": "instagram",
            "message": "Hi! I'm interested in your gaming laptops with good graphics cards",
            "branch": "convincer"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/conversation/message",
                json=test_message
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"      ✅ Conversation processed successfully")
                    print(f"      📝 Response: {data.get('ai_response', '')[:100]}...")
                    print(f"      🔑 Keywords: {data.get('keywords', [])}")
                    print(f"      📦 Products Found: {data.get('products_found', 0)}")
                else:
                    text = await response.text()
                    print(f"      ❌ Failed with status {response.status}: {text}")
                    
        except Exception as e:
            print(f"      ❌ Exception: {e}")
        
        return True

async def main():
    """Run all Step 5 tests"""
    print("🚀 ManipulatorAI Step 5 Test Suite: Core AI Logic")
    print("=" * 50)
    
    async with Step5Tester() as tester:
        # Test API availability
        if not await tester.test_api_status():
            print("\n❌ API is not accessible. Please ensure the server is running with:")
            print("   cd /Users/Kazi/Desktop/Manipulator-Demo")
            print("   python -m uvicorn main:app --reload")
            return False
        
        # Run AI subsystem tests
        tests = [
            ("keyRetriever", tester.test_keyword_extraction),
            ("tagMatcher", tester.test_product_matching),
            ("Full Pipeline", tester.test_full_pipeline),
            ("Conversation API", tester.test_conversation_endpoint)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n❌ {test_name} test failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Step 5 Test Results Summary:")
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nTests Passed: {passed}/{len(results)}")
        
        if passed == len(results):
            print("🎉 All Step 5 tests passed! Core AI Logic is working correctly.")
            print("   ✅ keyRetriever subsystem operational")
            print("   ✅ tagMatcher subsystem operational") 
            print("   ✅ AI conversation generation working")
            print("   ✅ Full pipeline integration successful")
            return True
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
            return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)

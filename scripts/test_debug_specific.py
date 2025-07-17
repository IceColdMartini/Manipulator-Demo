#!/usr/bin/env python3
"""
Debug specific test for failing endpoints
"""
import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8004"

async def test_ai_full_pipeline():
    """Test AI full pipeline endpoint with detailed error output"""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "message": "Looking for a powerful gaming laptop with good graphics card"
            }
            
            response = await client.post(
                f"{BASE_URL}/ai/full-pipeline",
                json=payload,
                timeout=30.0
            )
            
            print(f"AI Full Pipeline Test:")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"Error Response Text: {response.text}")
            else:
                data = response.json()
                print(f"Success Response: {json.dumps(data, indent=2)}")
                
    except Exception as e:
        print(f"Exception in AI Full Pipeline: {e}")
        print(f"Exception type: {type(e)}")


async def test_conversations_api():
    """Test conversations API endpoint with detailed error output"""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "customer_id": "test_customer_debug",
                "business_id": "test_business_debug", 
                "message": "Hi! I'm interested in your products",
                "platform": "facebook"
            }
            
            response = await client.post(
                f"{BASE_URL}/conversation/message",
                json=payload,
                timeout=30.0
            )
            
            print(f"\nConversations API Test:")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"Error Response Text: {response.text}")
            else:
                data = response.json()
                print(f"Success Response: {json.dumps(data, indent=2)}")
                
    except Exception as e:
        print(f"Exception in Conversations API: {e}")
        print(f"Exception type: {type(e)}")


async def main():
    print("🔍 Debug Testing for Failing Endpoints")
    print("=" * 50)
    
    await test_ai_full_pipeline()
    await test_conversations_api()


if __name__ == "__main__":
    asyncio.run(main())

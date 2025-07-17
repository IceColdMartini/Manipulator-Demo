#!/usr/bin/env python3
"""
Test conversations API specifically
"""
import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8004"

async def test_conversations_detailed():
    """Test conversations API with detailed error reporting"""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "customer_id": "test_customer_debug",
                "business_id": "test_business_debug", 
                "message": "Hi! I'm interested in your products",
                "platform": "facebook"
            }
            
            print("Testing Conversations API...")
            print(f"Request payload: {json.dumps(payload, indent=2)}")
            
            response = await client.post(
                f"{BASE_URL}/conversation/message",
                json=payload,
                timeout=60.0  # Longer timeout
            )
            
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"Error Response: {response.text}")
                
                # Try to get more details from response
                try:
                    error_data = response.json()
                    print(f"Error Details: {json.dumps(error_data, indent=2)}")
                except:
                    pass
                return False
                
    except Exception as e:
        print(f"Exception occurred: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_conversations_detailed())

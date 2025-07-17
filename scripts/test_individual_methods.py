#!/usr/bin/env python3
"""
Test individual methods to identify the specific issue
"""
import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8004"

async def test_ai_keyword_extraction():
    """Test AI keyword extraction - this works"""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "message": "Looking for a powerful gaming laptop with good graphics card"
            }
            
            response = await client.post(
                f"{BASE_URL}/ai/extract-keywords",
                json=payload,
                timeout=30.0
            )
            
            print(f"Keyword Extraction Test:")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Keywords: {data.get('extracted_keywords', [])}")
                return True
            else:
                print(f"Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"Exception: {e}")
        return False

async def test_ai_product_matching():
    """Test AI product matching - this works"""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "keywords": ["laptop", "gaming"],
                "threshold": 0.3
            }
            
            response = await client.post(
                f"{BASE_URL}/ai/match-products",
                json=payload,
                timeout=30.0
            )
            
            print(f"\nProduct Matching Test:")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Matches: {len(data.get('matches', []))}")
                return True
            else:
                print(f"Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"Exception: {e}")
        return False


async def main():
    print("🔍 Testing Individual Methods")
    print("=" * 50)
    
    success1 = await test_ai_keyword_extraction()
    success2 = await test_ai_product_matching()
    
    print(f"\nKeyword Extraction: {'✅' if success1 else '❌'}")
    print(f"Product Matching: {'✅' if success2 else '❌'}")


if __name__ == "__main__":
    asyncio.run(main())

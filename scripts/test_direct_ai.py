#!/usr/bin/env python3
"""
Direct test of Azure OpenAI keyword extraction
"""
import asyncio
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_service import AzureOpenAIService

async def test_direct_keyword_extraction():
    """Test the AI service directly"""
    try:
        ai_service = AzureOpenAIService()
        
        customer_message = "Looking for a powerful gaming laptop with good graphics card"
        business_context = "We sell electronics, fashion, and lifestyle products"
        
        print("Testing Azure OpenAI keyword extraction directly...")
        
        keywords = await ai_service.extract_keywords(customer_message, business_context)
        
        print(f"Success! Keywords extracted: {keywords}")
        return True
        
    except Exception as e:
        print(f"Error in direct test: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_direct_keyword_extraction())

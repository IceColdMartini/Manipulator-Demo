from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.ai_service import AzureOpenAIService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai-services"])

@router.post("/extract-keywords")
async def test_keyword_extraction(
    request_data: dict
):
    """
    Test the keyRetriever subsystem directly
    """
    try:
        customer_message = request_data.get("message", "")
        business_context = request_data.get("business_context", 
            "We sell electronics including smartphones, laptops, headphones, and fashion items like shirts.")
        
        if not customer_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        ai_service = AzureOpenAIService()
        keywords = await ai_service.extract_keywords(customer_message, business_context)
        
        return {
            "message": customer_message,
            "business_context": business_context,
            "extracted_keywords": keywords,
            "subsystem": "keyRetriever",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Keyword extraction test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract keywords: {str(e)}")

@router.post("/generate-response")
async def test_response_generation(
    request_data: dict
):
    """
    Test conversation response generation
    """
    try:
        customer_message = request_data.get("message", "")
        branch = request_data.get("branch", "convincer")
        is_welcome = request_data.get("is_welcome", True)
        
        if not customer_message and branch == "convincer":
            raise HTTPException(status_code=400, detail="Message is required for convincer branch")
        
        # Mock product data for testing
        mock_products = [
            {
                "product_description": "iPhone 15 Pro with 48MP Camera and A17 Pro Chip",
                "product_tag": ["iphone", "smartphone", "camera", "apple"],
                "product_attributes": {"price": "$999"}
            },
            {
                "product_description": "Dell XPS 15 Gaming Laptop with RTX 4060, Intel i7, 16GB RAM",
                "product_tag": ["laptop", "gaming", "programming", "dell"],
                "product_attributes": {"price": "$1499"}
            }
        ]
        
        context = {
            "branch": branch,
            "products": mock_products,
            "conversation_history": request_data.get("conversation_history", []),
            "interaction_type": request_data.get("interaction_type", "like")
        }
        
        ai_service = AzureOpenAIService()
        
        if branch == "convincer":
            response = await ai_service.generate_conversation_response(
                conversation_context=context,
                customer_message=customer_message,
                is_welcome=is_welcome
            )
        else:  # manipulator branch
            response = await ai_service.generate_conversation_response(
                conversation_context=context,
                is_welcome=is_welcome
            )
        
        return {
            "customer_message": customer_message,
            "branch": branch,
            "is_welcome": is_welcome,
            "ai_response": response,
            "context": {
                "products_count": len(mock_products),
                "interaction_type": context.get("interaction_type")
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Response generation test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

@router.post("/full-pipeline")
async def test_full_ai_pipeline(
    request_data: dict
):
    """
    Test the complete keyRetriever → AI Response pipeline (simplified)
    """
    try:
        customer_message = request_data.get("message", "")
        business_context = request_data.get("business_context",
            "We sell electronics including smartphones, laptops, headphones, and fashion items.")
        branch = request_data.get("branch", "convincer")
        
        if not customer_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Initialize AI service
        ai_service = AzureOpenAIService()
        
        # Step 1: keyRetriever
        logger.info("Step 1: Running keyRetriever...")
        keywords = await ai_service.extract_keywords(customer_message, business_context)
        
        # Step 2: Mock product matching (since we don't have DB dependency)
        logger.info("Step 2: Simulating product matching...")
        mock_matches = []
        
        # Simple keyword matching simulation
        all_products = [
            {
                "product_description": "iPhone 15 Pro with 48MP Camera and A17 Pro Chip",
                "product_tag": ["iphone", "smartphone", "camera", "apple", "phone", "mobile"],
                "product_attributes": {"price": "$999"}
            },
            {
                "product_description": "Dell XPS 15 Gaming Laptop with RTX 4060, Intel i7, 16GB RAM",
                "product_tag": ["laptop", "gaming", "programming", "dell", "computer"],
                "product_attributes": {"price": "$1499"}
            },
            {
                "product_description": "Sony WH-1000XM4 Wireless Noise Canceling Headphones",
                "product_tag": ["headphones", "wireless", "bluetooth", "audio", "sony"],
                "product_attributes": {"price": "$349"}
            },
            {
                "product_description": "Samsung Galaxy S24 Ultra with S Pen",
                "product_tag": ["smartphone", "samsung", "android", "phone", "stylus"],
                "product_attributes": {"price": "$1199"}
            }
        ]
        
        # Find matching products based on keywords
        for product in all_products:
            score = 0
            for keyword in keywords:
                if any(keyword.lower() in tag.lower() for tag in product["product_tag"]):
                    score += 0.3
                if keyword.lower() in product["product_description"].lower():
                    score += 0.4
            
            if score > 0:
                mock_matches.append({
                    "product": product,
                    "score": min(score, 1.0)
                })
        
        # Sort by score and take top 3
        mock_matches.sort(key=lambda x: x["score"], reverse=True)
        top_matches = mock_matches[:3]
        
        # Step 3: AI Response Generation
        logger.info("Step 3: Generating AI response...")
        context = {
            "branch": branch,
            "products": [match["product"] for match in top_matches],
            "keywords": keywords,
            "conversation_history": []
        }
        
        ai_response = await ai_service.generate_conversation_response(
            context, customer_message, is_welcome=True
        )
        
        return {
            "customer_message": customer_message,
            "step_1_keywords": keywords,
            "step_2_matches": len(top_matches),
            "step_2_products": [
                {
                    "score": match["score"],
                    "product_name": match["product"]["product_description"][:40] + "..."
                }
                for match in top_matches
            ],
            "step_3_ai_response": ai_response,
            "pipeline_status": "complete",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Full AI pipeline test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run AI pipeline: {str(e)}")

@router.get("/health")
async def ai_health_check():
    """
    Health check for AI services
    """
    try:
        ai_service = AzureOpenAIService()
        
        # Test basic connectivity
        test_response = await ai_service.generate_completion(
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5,
            temperature=0.1
        )
        
        return {
            "status": "healthy",
            "azure_openai": "connected",
            "test_response": test_response[:50] + "..." if len(test_response) > 50 else test_response
        }
        
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "azure_openai": "disconnected",
            "error": str(e)
        }

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.core.database import get_postgres_session
from app.services.ai_service import AzureOpenAIService
from app.services.product_service import ProductService
from sqlalchemy.ext.asyncio import AsyncSession
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
            "subsystem": "keyRetriever"
        }
        
    except Exception as e:
        logger.error(f"Keyword extraction test failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract keywords")

@router.post("/match-products")
async def test_product_matching(
    request_data: dict,
    postgres_session: AsyncSession = Depends(get_postgres_session)
):
    """
    Test the tagMatcher subsystem directly
    """
    try:
        keywords = request_data.get("keywords", [])
        threshold = request_data.get("threshold", 0.3)
        
        if not keywords:
            raise HTTPException(status_code=400, detail="Keywords are required")
        
        product_service = ProductService(postgres_session)
        matches = await product_service.search_products_by_tags(keywords, threshold)
        
        return {
            "keywords": keywords,
            "threshold": threshold,
            "matches_found": len(matches),
            "matches": [
                {
                    "product_id": match["product_id"],
                    "score": match["score"],
                    "product_name": match["product"].product_description[:50] + "...",
                    "product_tags": match["product"].product_tag
                }
                for match in matches
            ],
            "subsystem": "tagMatcher"
        }
        
    except Exception as e:
        logger.error(f"Product matching test failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to match products")

@router.post("/full-pipeline")
async def test_full_ai_pipeline(
    request_data: dict,
    postgres_session: AsyncSession = Depends(get_postgres_session)
):
    """
    Test the complete keyRetriever → tagMatcher → AI Response pipeline
    """
    try:
        customer_message = request_data.get("message", "")
        business_context = request_data.get("business_context",
            "We sell electronics including smartphones, laptops, headphones, and fashion items.")
        
        if not customer_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Initialize services
        ai_service = AzureOpenAIService()
        product_service = ProductService(postgres_session)
        
        # Step 1: keyRetriever
        logger.info("Step 1: Running keyRetriever...")
        keywords = await ai_service.extract_keywords(customer_message, business_context)
        
        # Step 2: tagMatcher
        logger.info("Step 2: Running tagMatcher...")
        matches = await product_service.search_products_by_tags(keywords, threshold=0.3)
        
        # Step 3: AI Response Generation
        logger.info("Step 3: Generating AI response...")
        context = {
            "branch": "convincer",
            "products": [match["product"].dict() for match in matches[:3]],
            "keywords": keywords,
            "conversation_history": []
        }
        
        ai_response = await ai_service.generate_conversation_response(
            context, customer_message, is_welcome=True
        )
        
        return {
            "customer_message": customer_message,
            "step_1_keywords": keywords,
            "step_2_matches": len(matches),
            "step_2_products": [
                {
                    "score": match["score"],
                    "product_name": match["product"].product_description[:40] + "..."
                }
                for match in matches[:3]
            ],
            "step_3_ai_response": ai_response,
            "pipeline_status": "complete"
        }
        
    except Exception as e:
        logger.error(f"Full AI pipeline test failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to run AI pipeline")

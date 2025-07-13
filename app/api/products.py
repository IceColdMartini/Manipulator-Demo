from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.schemas import Product, ProductCreate
from app.core.database import get_postgres_session
from app.services.product_service import ProductService
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[Product])
async def get_all_products(
    postgres_session: AsyncSession = Depends(get_postgres_session)
):
    """Get all products in the knowledge base"""
    try:
        product_service = ProductService(postgres_session)
        products = await product_service.get_all_products()
        return products
        
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve products")

@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    postgres_session: AsyncSession = Depends(get_postgres_session)
):
    """Get a specific product by ID"""
    try:
        product_service = ProductService(postgres_session)
        product = await product_service.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve product")

@router.post("/", response_model=Product)
async def create_product(
    product_data: ProductCreate,
    postgres_session: AsyncSession = Depends(get_postgres_session)
):
    """Create a new product"""
    try:
        product_service = ProductService(postgres_session)
        product = await product_service.create_product(product_data)
        return product
        
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")

@router.post("/search")
async def search_products(
    keywords: List[str],
    threshold: float = 0.8,
    postgres_session: AsyncSession = Depends(get_postgres_session)
):
    """
    Search products by keywords - This is the tagMatcher functionality
    """
    try:
        product_service = ProductService(postgres_session)
        matches = await product_service.search_products_by_tags(keywords, threshold)
        
        return {
            "keywords": keywords,
            "threshold": threshold,
            "results": [
                {
                    "product_id": match["product_id"],
                    "score": match["score"],
                    "product": match["product"]
                }
                for match in matches
            ]
        }
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail="Failed to search products")

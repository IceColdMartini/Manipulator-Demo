from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.database import ProductModel
from app.models.schemas import Product, ProductCreate, ProductAttributes
import uuid
import logging

logger = logging.getLogger(__name__)

class ProductService:
    """Service class for product-related database operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        try:
            db_product = ProductModel(
                name=product_data.name,
                description=product_data.description,
                price=product_data.price,
                currency=product_data.currency,
                category=product_data.category,
                product_metadata=product_data.metadata
            )
            
            self.session.add(db_product)
            await self.session.commit()
            await self.session.refresh(db_product)
            
            return self._to_pydantic(db_product)
            
        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            await self.session.rollback()
            raise
    
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a product by its ID"""
        try:
            query = select(ProductModel).where(ProductModel.id == uuid.UUID(product_id))
            result = await self.session.execute(query)
            db_product = result.scalar_one_or_none()
            
            if db_product:
                return self._to_pydantic(db_product)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get product {product_id}: {e}")
            raise
    
    async def get_products_by_ids(self, product_ids: List[str]) -> List[Product]:
        """Get multiple products by their IDs"""
        try:
            uuid_ids = [uuid.UUID(pid) for pid in product_ids]
            query = select(ProductModel).where(ProductModel.id.in_(uuid_ids))
            result = await self.session.execute(query)
            db_products = result.scalars().all()
            
            return [self._to_pydantic(product) for product in db_products]
            
        except Exception as e:
            logger.error(f"Failed to get products {product_ids}: {e}")
            raise
    
    async def search_products_by_keywords(self, keywords: List[str]) -> List[Product]:
        """Search products by keywords in name and description."""
        try:
            clauses = []
            for keyword in keywords:
                clauses.append(ProductModel.name.ilike(f"%{keyword}%"))
                clauses.append(ProductModel.description.ilike(f"%{keyword}%"))
            
            query = select(ProductModel).where(or_(*clauses))
            result = await self.session.execute(query)
            db_products = result.scalars().all()
            
            return [self._to_pydantic(product) for product in db_products]
            
        except Exception as e:
            logger.error(f"Failed to search products by keywords: {e}")
            raise
    
    async def get_all_products(self) -> List[Product]:
        """Get all products"""
        try:
            query = select(ProductModel)
            result = await self.session.execute(query)
            db_products = result.scalars().all()
            
            return [self._to_pydantic(product) for product in db_products]
            
        except Exception as e:
            logger.error(f"Failed to get all products: {e}")
            raise
            
    def _calculate_tag_similarity(self, keywords: List[str], product_tags: List[str]) -> float:
        """
        Calculate similarity score between keywords and product tags
        Simple implementation using Jaccard similarity
        """
        if not keywords or not product_tags:
            return 0.0
        
        # Convert to lowercase for comparison
        keywords_lower = set(word.lower() for word in keywords)
        tags_lower = set(tag.lower() for tag in product_tags)
        
        # Calculate Jaccard similarity
        intersection = keywords_lower.intersection(tags_lower)
        union = keywords_lower.union(tags_lower)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _to_pydantic(self, db_product: ProductModel) -> Product:
        """Convert SQLAlchemy model to Pydantic model"""
        return Product(
            id=str(db_product.id),
            name=db_product.name,
            description=db_product.description,
            price=db_product.price,
            currency=db_product.currency,
            category=db_product.category,
            metadata=db_product.product_metadata
        )

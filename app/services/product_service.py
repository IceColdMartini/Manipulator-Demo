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
                product_attributes=product_data.product_attributes.dict(),
                product_tag=product_data.product_tag,
                product_description=product_data.product_description
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
            query = select(ProductModel).where(ProductModel.product_id == uuid.UUID(product_id))
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
            query = select(ProductModel).where(ProductModel.product_id.in_(uuid_ids))
            result = await self.session.execute(query)
            db_products = result.scalars().all()
            
            return [self._to_pydantic(product) for product in db_products]
            
        except Exception as e:
            logger.error(f"Failed to get products {product_ids}: {e}")
            raise
    
    async def search_products_by_tags(self, keywords: List[str], threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Search products by tags with similarity scoring
        Returns list of dictionaries with product_id and score
        """
        try:
            # Get all products
            query = select(ProductModel)
            result = await self.session.execute(query)
            all_products = result.scalars().all()
            
            matches = []
            for product in all_products:
                # Calculate similarity score
                score = self._calculate_tag_similarity(keywords, product.product_tag)
                if score >= threshold:
                    matches.append({
                        'product_id': str(product.product_id),
                        'score': score,
                        'product': self._to_pydantic(product)
                    })
            
            # Sort by score descending
            matches.sort(key=lambda x: x['score'], reverse=True)
            return matches
            
        except Exception as e:
            logger.error(f"Failed to search products by tags: {e}")
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
            product_id=str(db_product.product_id),
            product_attributes=ProductAttributes(**db_product.product_attributes),
            product_tag=db_product.product_tag,
            product_description=db_product.product_description,
            created_at=db_product.created_at,
            updated_at=db_product.updated_at
        )

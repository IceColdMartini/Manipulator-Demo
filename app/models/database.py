from sqlalchemy import Column, String, Text, ARRAY, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

Base = declarative_base()

class ProductModel(Base):
    __tablename__ = "products"
    
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_attributes = Column(JSONB, nullable=False)
    product_tag = Column(ARRAY(Text), nullable=False)
    product_description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Product(id={self.product_id}, tags={self.product_tag})>"

"""
Database table definitions
"""
from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, MetaData

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("email", String, unique=True, index=True, nullable=False),
    Column("full_name", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("updated_at", DateTime, onupdate=datetime.utcnow)
)

# Product knowledge base
products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=False),
    Column("features", String, nullable=False),  # JSON string
    Column("price", Integer, nullable=False),  # Price in cents
    Column("category", String, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("updated_at", DateTime, onupdate=datetime.utcnow)
)

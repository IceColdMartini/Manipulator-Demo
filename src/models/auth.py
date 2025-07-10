"""
Authentication models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8)

class User(UserBase):
    """User schema"""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

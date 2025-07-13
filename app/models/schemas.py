from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums for better type safety
class InteractionType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    CLICK = "click"
    MESSAGE = "message"

class ConversationBranch(str, Enum):
    MANIPULATOR = "manipulator"
    CONVINCER = "convincer"

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    QUALIFIED = "qualified"
    UNINTERESTED = "uninterested"
    TRANSFERRED = "transferred"

class MessageSender(str, Enum):
    AGENT = "agent"
    CUSTOMER = "customer"

# API Request/Response Models
class FacebookWebhookPayload(BaseModel):
    object: str
    entry: List[Dict[str, Any]]

class InstagramWebhookPayload(BaseModel):
    object: str
    entry: List[Dict[str, Any]]

class CustomerMessage(BaseModel):
    customer_id: str
    business_id: str
    message: str
    platform: str = Field(..., description="facebook or instagram")
    timestamp: Optional[datetime] = None

class ConversationMessage(BaseModel):
    timestamp: datetime
    sender: MessageSender
    content: str
    intent: Optional[str] = None
    sentiment: Optional[str] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    response: str
    status: ConversationStatus
    next_action: Optional[str] = None

# Product Models
class ProductAttributes(BaseModel):
    price: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    # Allow additional dynamic attributes
    
    class Config:
        extra = "allow"

class Product(BaseModel):
    product_id: str
    product_attributes: ProductAttributes
    product_tag: List[str]
    product_description: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProductCreate(BaseModel):
    product_attributes: ProductAttributes
    product_tag: List[str]
    product_description: str

# Conversation Models
class Conversation(BaseModel):
    conversation_id: str
    customer_id: str
    business_id: str
    product_context: List[str]  # List of product IDs
    conversation_branch: ConversationBranch
    messages: List[ConversationMessage]
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime

class ConversationCreate(BaseModel):
    customer_id: str
    business_id: str
    product_context: List[str]
    conversation_branch: ConversationBranch

# Service Models for Internal Logic
class KeywordExtractionRequest(BaseModel):
    message: str
    business_context: str

class KeywordExtractionResponse(BaseModel):
    keywords: List[str]

class ProductMatchRequest(BaseModel):
    keywords: List[str]
    correlation_threshold: float = 0.8

class ProductMatchResponse(BaseModel):
    product_id: str
    score: float

class ConversationContext(BaseModel):
    conversation_id: str
    customer_id: str
    business_id: str
    products: List[Product]
    conversation_history: List[ConversationMessage]
    current_branch: ConversationBranch
    is_first_interaction: bool = True

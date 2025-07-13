from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from app.models.schemas import (
    CustomerMessage, ConversationResponse, Conversation,
    ConversationCreate, ConversationBranch, ConversationMessage,
    MessageSender
)
from app.core.database import get_postgres_session, get_mongo_db, get_redis_client
from app.services.product_service import ProductService
from app.services.conversation_service import ConversationService
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation", tags=["conversations"])

@router.post("/message", response_model=ConversationResponse)
async def process_customer_message(
    message: CustomerMessage,
    background_tasks: BackgroundTasks,
    postgres_session: AsyncSession = Depends(get_postgres_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    redis_client = Depends(get_redis_client)
):
    """
    Process incoming customer message - This is the entry point for the Convincer branch
    """
    try:
        logger.info(f"Processing message from customer {message.customer_id}: {message.message[:50]}...")
        
        # Initialize services
        product_service = ProductService(postgres_session)
        conversation_service = ConversationService(mongo_db)
        
        # Check for existing active conversation
        existing_conversations = await conversation_service.get_active_conversations_for_customer(
            message.customer_id
        )
        
        if existing_conversations:
            # Continue existing conversation
            conversation = existing_conversations[0]
            logger.info(f"Continuing existing conversation: {conversation.conversation_id}")
        else:
            # This is the Convincer branch - need to extract keywords and find products
            # For now, we'll create a conversation with empty product context
            # In Step 5, we'll implement the keyRetriever and tagMatcher logic
            conversation_data = ConversationCreate(
                customer_id=message.customer_id,
                business_id=message.business_id,
                product_context=[],  # Will be populated by keyRetriever + tagMatcher
                conversation_branch=ConversationBranch.CONVINCER
            )
            
            conversation = await conversation_service.create_conversation(conversation_data)
            logger.info(f"Created new conversation: {conversation.conversation_id}")
        
        # Add customer message to conversation
        customer_msg = ConversationMessage(
            timestamp=message.timestamp or datetime.now(),
            sender=MessageSender.CUSTOMER,
            content=message.message,
            intent="inquiry"
        )
        
        await conversation_service.add_message(conversation.conversation_id, customer_msg)
        
        # Queue message for AI processing
        await redis_client.lpush("ai_processing_queue", json.dumps({
            "conversation_id": conversation.conversation_id,
            "customer_message": message.message,
            "timestamp": datetime.now().isoformat(),
            "branch": "convincer"
        }))
        
        # For now, return a placeholder response
        # In Step 6, this will be replaced with actual AI-generated responses
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            response="Thank you for your message! Our AI agent is processing your request and will respond shortly.",
            status=conversation.status,
            next_action="ai_processing"
        )
        
    except Exception as e:
        logger.error(f"Error processing customer message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """Get conversation by ID"""
    try:
        conversation_service = ConversationService(mongo_db)
        conversation = await conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return conversation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")

@router.get("/{conversation_id}/history", response_model=List[ConversationMessage])
async def get_conversation_history(
    conversation_id: str,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """Get conversation message history"""
    try:
        conversation_service = ConversationService(mongo_db)
        messages = await conversation_service.get_conversation_history(conversation_id)
        
        return messages
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation history")

@router.post("/webhook-interaction")
async def process_webhook_interaction(
    interaction_data: dict,
    background_tasks: BackgroundTasks,
    postgres_session: AsyncSession = Depends(get_postgres_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    redis_client = Depends(get_redis_client)
):
    """
    Process webhook interaction data - This is the entry point for the Manipulator branch
    """
    try:
        logger.info(f"Processing webhook interaction: {interaction_data}")
        
        # Extract interaction details
        customer_id = interaction_data.get("customer_id", "unknown_customer")
        business_id = interaction_data.get("business_id", "unknown_business")
        product_id = interaction_data.get("product_id")
        interaction_type = interaction_data.get("interaction_type", "unknown")
        
        if not product_id:
            raise HTTPException(status_code=400, detail="Product ID is required for webhook interactions")
        
        # Initialize services
        product_service = ProductService(postgres_session)
        conversation_service = ConversationService(mongo_db)
        
        # Verify product exists
        product = await product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Create conversation for Manipulator branch
        conversation_data = ConversationCreate(
            customer_id=customer_id,
            business_id=business_id,
            product_context=[product_id],  # Direct product context from interaction
            conversation_branch=ConversationBranch.MANIPULATOR
        )
        
        conversation = await conversation_service.create_conversation(conversation_data)
        logger.info(f"Created manipulator conversation: {conversation.conversation_id}")
        
        # Queue for AI processing
        await redis_client.lpush("ai_processing_queue", json.dumps({
            "conversation_id": conversation.conversation_id,
            "product_id": product_id,
            "interaction_type": interaction_type,
            "timestamp": datetime.now().isoformat(),
            "branch": "manipulator"
        }))
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            response="Hello! I noticed you showed interest in our product. Let me help you learn more about it!",
            status=conversation.status,
            next_action="ai_processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to process interaction")

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from app.models.schemas import (
    CustomerMessage, ConversationResponse, Conversation,
    ConversationCreate, ConversationBranch, ConversationMessage,
    MessageSender
)
from app.core.database import get_postgres_session, get_mongo_db, get_redis_client
from app.services.product_service import ProductService
from app.services.conversation_service import ConversationService
from app.services.ai_service import AzureOpenAIService
from app.services.enhanced_conversation_engine import EnhancedConversationEngine
from app.services.task_manager import task_manager
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation", tags=["conversations"])

def get_conversation_engine(
    postgres_session: AsyncSession = Depends(get_postgres_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> EnhancedConversationEngine:
    """Dependency to get enhanced conversation engine with all services"""
    ai_service = AzureOpenAIService()
    product_service = ProductService(postgres_session)
    conversation_service = ConversationService(mongo_db)
    
    return EnhancedConversationEngine(ai_service, product_service, conversation_service)

@router.post("/message", response_model=ConversationResponse)
async def process_customer_message(
    message: CustomerMessage,
    background_tasks: BackgroundTasks,
    conversation_engine: EnhancedConversationEngine = Depends(get_conversation_engine),
    redis_client = Depends(get_redis_client),
    async_processing: bool = False
):
    """
    Process incoming customer message - Enhanced with async task processing
    Set async_processing=True for background processing
    """
    try:
        print(f"🔍 DEBUG: Conversation endpoint hit with customer_id={message.customer_id}")
        logger.info(f"Processing message from customer {message.customer_id}: {message.message[:50]}...")
        logger.info(f"Message details: customer_id={message.customer_id}, business_id={message.business_id}, platform={message.platform}")
        
        # If async processing is requested, queue the task
        if async_processing:
            task_id = task_manager.process_customer_message_async(
                customer_id=message.customer_id,
                business_id=message.business_id,
                message=message.message,
                message_metadata={
                    "timestamp": message.timestamp.isoformat() if message.timestamp else datetime.utcnow().isoformat(),
                    "channel": "api",
                    "async_requested": True
                }
            )
            
            return ConversationResponse(
                conversation_id="pending",
                response=f"Your message is being processed. Task ID: {task_id}",
                status="processing",
                next_action="check_task_status",
                task_id=task_id
            )
        
        # Otherwise, process synchronously (existing behavior)
        # Check for existing active conversation
        existing_conversations = await conversation_engine.conversation_service.get_active_conversations_for_customer(
            message.customer_id
        )
        
        if existing_conversations:
            # Continue existing conversation using enhanced engine
            conversation = existing_conversations[0]
            logger.info(f"Continuing existing conversation: {conversation.conversation_id}")
            
            # Use enhanced conversation engine for continuation
            result = await conversation_engine.continue_conversation(
                conversation.conversation_id,
                message.message,
                {"timestamp": message.timestamp}
            )
            
            ai_response = result.get("ai_response", "I'm here to help you.")
            status = result.get("conversation_status", "active")
            
        else:
            # Start new Convincer conversation using enhanced engine
            logger.info(f"Starting new Convincer conversation for customer {message.customer_id}")
            
            result = await conversation_engine.start_convincer_conversation(
                customer_id=message.customer_id,
                business_id=message.business_id,
                initial_message=message.message,
                customer_context={"timestamp": message.timestamp}
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error", "Failed to start conversation"))
            
            conversation_id = result.get("conversation_id")
            ai_response = result.get("ai_response", "Hello! How can I help you today?")
            status = result.get("conversation_status", "active")
            
            # Get conversation object for response
            conversation = await conversation_engine.conversation_service.get_conversation(conversation_id)
        
        return ConversationResponse(
            conversation_id=conversation_id if 'conversation_id' in locals() else conversation.conversation_id,
            response=ai_response,
            status=status if 'status' in locals() else conversation.status,
            next_action="conversation_active"
        )
        
    except Exception as e:
        logger.error(f"Error processing customer message: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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

@router.post("/{conversation_id}/continue", response_model=ConversationResponse)
async def continue_conversation(
    conversation_id: str,
    message_data: dict,
    conversation_engine: EnhancedConversationEngine = Depends(get_conversation_engine)
):
    """
    Continue an existing conversation with a new customer message
    """
    try:
        customer_message = message_data.get("message", "")
        if not customer_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Use enhanced conversation engine for continuation
        result = await conversation_engine.continue_conversation(
            conversation_id,
            customer_message,
            {"timestamp": datetime.now()}
        )
        
        ai_response = result.get("ai_response", "I'm here to help you.")
        status = result.get("conversation_status", "active")
        
        return ConversationResponse(
            conversation_id=conversation_id,
            response=ai_response,
            status=status,
            next_action="conversation_active"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error continuing conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to continue conversation")

@router.post("/webhook-interaction")
async def process_webhook_interaction(
    interaction_data: dict,
    background_tasks: BackgroundTasks,
    conversation_engine: EnhancedConversationEngine = Depends(get_conversation_engine),
    redis_client = Depends(get_redis_client),
    async_processing: bool = True  # Default to async for webhooks
):
    """
    Process webhook interaction data - Enhanced with async task processing
    Webhooks default to async processing to ensure fast response times
    """
    try:
        logger.info(f"Processing webhook interaction: {interaction_data}")
        
        # Extract interaction details
        customer_id = interaction_data.get("customer_id", "unknown_customer")
        business_id = interaction_data.get("business_id", "unknown_business")
        product_id = interaction_data.get("product_id")
        interaction_type = interaction_data.get("interaction_type", "unknown")
        platform = interaction_data.get("platform", "unknown")
        
        # For async processing, queue the task immediately
        if async_processing:
            task_id = task_manager.process_webhook_async(
                webhook_data=interaction_data,
                platform=platform,
                priority="high"  # Webhooks get high priority
            )
            
            return ConversationResponse(
                conversation_id="pending",
                response="Webhook received and being processed",
                status="processing",
                next_action="webhook_processed",
                task_id=task_id
            )
        
        # Synchronous processing (fallback)
        if not product_id:
            raise HTTPException(status_code=400, detail="Product ID is required for webhook interactions")
        
        # Verify product exists
        product = await conversation_engine.product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Start Manipulator conversation using enhanced engine
        result = await conversation_engine.start_manipulator_conversation(
            customer_id=customer_id,
            business_id=business_id,
            interaction_data={
                "product_id": product_id,
                "type": interaction_type,
                "platform": platform
            }
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to start conversation"))
        
        conversation_id = result.get("conversation_id")
        ai_response = result.get("ai_response", "Welcome! I'd love to help you with this product.")
        status = "active"
        
        return ConversationResponse(
            conversation_id=conversation_id,
            response=ai_response,
            status=status,
            next_action="conversation_active"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to process interaction")


# Task Status Monitoring Endpoints
@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """
    Get the status of an async task
    """
    try:
        status_info = task_manager.get_task_status(task_id)
        
        if not status_info:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "task_id": task_id,
            "status": status_info.get("status"),
            "progress": status_info.get("progress"),
            "result": status_info.get("result"),
            "error": status_info.get("error"),
            "created_at": status_info.get("created_at"),
            "updated_at": status_info.get("updated_at")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tasks/queues/status")
async def get_queue_status():
    """
    Get the status of all task queues
    """
    try:
        queue_stats = task_manager.get_queue_statistics()
        
        return {
            "queues": queue_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tasks/active")
async def get_active_tasks():
    """
    Get list of currently active tasks
    """
    try:
        active_tasks = task_manager.get_active_tasks()
        
        return {
            "active_tasks": active_tasks,
            "count": len(active_tasks),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting active tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """
    Cancel a running task
    """
    try:
        success = task_manager.cancel_task(task_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancelled successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

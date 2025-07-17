"""
Conversation Tasks for Asynchronous Processing
Handles conversation-related operations in the background
"""

from celery import current_task
from app.core.celery_app import celery_app
from app.core.database import get_postgres_session, get_mongo_db, get_redis_client
from app.core.config import settings
from app.services.enhanced_conversation_engine import EnhancedConversationEngine
from app.services.ai_service import AzureOpenAIService
from app.services.product_service import ProductService
from app.services.conversation_service import ConversationService
from typing import Dict, Any, Optional
import asyncio
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def run_async_task(coro):
    """Helper to run async functions in Celery tasks"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

@celery_app.task(bind=True, name="process_conversation_message")
def process_conversation_message_task(
    self,
    customer_id: str,
    business_id: str,
    message: str,
    message_metadata: Optional[Dict[str, Any]] = None
):
    """
    Asynchronously process customer conversation messages
    """
    try:
        task_id = self.request.id
        logger.info(f"Processing conversation message task {task_id} for customer {customer_id}")
        
        # Update task status
        self.update_state(
            state="PROCESSING",
            meta={
                "customer_id": customer_id,
                "business_id": business_id,
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        async def process_message():
            # Initialize services
            ai_service = AzureOpenAIService()
            
            # Create database sessions
            from app.core.database import async_session_maker, get_mongo_client
            
            async with async_session_maker() as postgres_session:
                mongo_client = get_mongo_client()
                mongo_db = mongo_client[settings.MONGO_DB_NAME]
                
                product_service = ProductService(postgres_session)
                conversation_service = ConversationService(mongo_db)
                
                # Initialize enhanced conversation engine
                engine = EnhancedConversationEngine(
                    ai_service=ai_service,
                    product_service=product_service,
                    conversation_service=conversation_service
                )
                
                # Update progress
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "customer_id": customer_id,
                        "business_id": business_id,
                        "progress": 25,
                        "status": "Services initialized"
                    }
                )
                
                # Check for existing conversation
                existing_conversations = await conversation_service.get_active_conversations_for_customer(
                    customer_id
                )
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "customer_id": customer_id,
                        "business_id": business_id,
                        "progress": 50,
                        "status": "Checked existing conversations"
                    }
                )
                
                if existing_conversations:
                    # Continue existing conversation
                    conversation = existing_conversations[0]
                    result = await engine.continue_conversation(
                        conversation_id=conversation.conversation_id,
                        customer_message=message,
                        customer_context=message_metadata or {}
                    )
                else:
                    # Start new convincer conversation
                    result = await engine.start_convincer_conversation(
                        customer_id=customer_id,
                        business_id=business_id,
                        initial_message=message,
                        customer_context=message_metadata or {}
                    )
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "customer_id": customer_id,
                        "business_id": business_id,
                        "progress": 90,
                        "status": "Generated AI response"
                    }
                )
                
                return result
        
        # Run the async process
        result = run_async_task(process_message())
        
        # Final success state
        self.update_state(
            state="SUCCESS",
            meta={
                "customer_id": customer_id,
                "business_id": business_id,
                "progress": 100,
                "status": "Completed successfully",
                "completed_at": datetime.utcnow().isoformat(),
                "result": result
            }
        )
        
        logger.info(f"Successfully processed conversation message task {task_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in conversation message task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "customer_id": customer_id,
                "business_id": business_id,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

@celery_app.task(bind=True, name="process_manipulator_interaction")
def process_manipulator_interaction_task(
    self,
    customer_id: str,
    business_id: str,
    interaction_data: Dict[str, Any]
):
    """
    Asynchronously process manipulator branch interactions from ads/webhooks
    """
    try:
        task_id = self.request.id
        logger.info(f"Processing manipulator interaction task {task_id} for customer {customer_id}")
        
        # Update task status
        self.update_state(
            state="PROCESSING",
            meta={
                "customer_id": customer_id,
                "business_id": business_id,
                "interaction_type": interaction_data.get("type", "unknown"),
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        async def process_interaction():
            # Initialize services
            ai_service = AzureOpenAIService()
            
            from app.core.database import async_session_maker, get_mongo_client
            from app.core.config import settings
            
            async with async_session_maker() as postgres_session:
                mongo_client = get_mongo_client()
                mongo_db = mongo_client[settings.MONGO_DB_NAME]
                
                product_service = ProductService(postgres_session)
                conversation_service = ConversationService(mongo_db)
                
                # Initialize enhanced conversation engine
                engine = EnhancedConversationEngine(
                    ai_service=ai_service,
                    product_service=product_service,
                    conversation_service=conversation_service
                )
                
                # Update progress
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "customer_id": customer_id,
                        "business_id": business_id,
                        "progress": 30,
                        "status": "Services initialized"
                    }
                )
                
                # Validate product if provided
                product_id = interaction_data.get("product_id")
                if product_id:
                    product = await product_service.get_product_by_id(product_id)
                    if not product:
                        raise ValueError(f"Product {product_id} not found")
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "customer_id": customer_id,
                        "business_id": business_id,
                        "progress": 60,
                        "status": "Product validated"
                    }
                )
                
                # Start manipulator conversation
                result = await engine.start_manipulator_conversation(
                    customer_id=customer_id,
                    business_id=business_id,
                    interaction_data=interaction_data
                )
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "customer_id": customer_id,
                        "business_id": business_id,
                        "progress": 90,
                        "status": "Generated welcome response"
                    }
                )
                
                return result
        
        # Run the async process
        result = run_async_task(process_interaction())
        
        # Final success state
        self.update_state(
            state="SUCCESS",
            meta={
                "customer_id": customer_id,
                "business_id": business_id,
                "progress": 100,
                "status": "Completed successfully",
                "completed_at": datetime.utcnow().isoformat(),
                "result": result
            }
        )
        
        logger.info(f"Successfully processed manipulator interaction task {task_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in manipulator interaction task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "customer_id": customer_id,
                "business_id": business_id,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

@celery_app.task(bind=True, name="continue_conversation_async")
def continue_conversation_async_task(
    self,
    conversation_id: str,
    customer_message: str,
    customer_context: Optional[Dict[str, Any]] = None
):
    """
    Asynchronously continue an existing conversation
    """
    try:
        task_id = self.request.id
        logger.info(f"Continuing conversation task {task_id} for conversation {conversation_id}")
        
        self.update_state(
            state="PROCESSING",
            meta={
                "conversation_id": conversation_id,
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        async def continue_conversation():
            # Initialize services
            ai_service = AzureOpenAIService()
            
            from app.core.database import async_session_maker, get_mongo_client
            from app.core.config import settings
            
            async with async_session_maker() as postgres_session:
                mongo_client = get_mongo_client()
                mongo_db = mongo_client[settings.MONGO_DB_NAME]
                
                product_service = ProductService(postgres_session)
                conversation_service = ConversationService(mongo_db)
                
                # Initialize enhanced conversation engine
                engine = EnhancedConversationEngine(
                    ai_service=ai_service,
                    product_service=product_service,
                    conversation_service=conversation_service
                )
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "conversation_id": conversation_id,
                        "progress": 50,
                        "status": "Services initialized"
                    }
                )
                
                # Continue the conversation
                result = await engine.continue_conversation(
                    conversation_id=conversation_id,
                    customer_message=customer_message,
                    customer_context=customer_context or {}
                )
                
                return result
        
        # Run the async process
        result = run_async_task(continue_conversation())
        
        # Final success state
        self.update_state(
            state="SUCCESS",
            meta={
                "conversation_id": conversation_id,
                "progress": 100,
                "status": "Completed successfully",
                "completed_at": datetime.utcnow().isoformat(),
                "result": result
            }
        )
        
        logger.info(f"Successfully continued conversation task {task_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in continue conversation task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "conversation_id": conversation_id,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

@celery_app.task(bind=True, name="batch_conversation_analysis")
def batch_conversation_analysis_task(self, conversation_ids: list):
    """
    Asynchronously analyze multiple conversations for insights
    """
    try:
        task_id = self.request.id
        logger.info(f"Batch conversation analysis task {task_id} for {len(conversation_ids)} conversations")
        
        self.update_state(
            state="PROCESSING",
            meta={
                "total_conversations": len(conversation_ids),
                "processed": 0,
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        async def analyze_conversations():
            from app.core.database import async_session_maker, get_mongo_client
            from app.core.config import settings
            
            async with async_session_maker() as postgres_session:
                mongo_client = get_mongo_client()
                mongo_db = mongo_client[settings.MONGO_DB_NAME]
                
                product_service = ProductService(postgres_session)
                conversation_service = ConversationService(mongo_db)
                ai_service = AzureOpenAIService()
                
                engine = EnhancedConversationEngine(
                    ai_service=ai_service,
                    product_service=product_service,
                    conversation_service=conversation_service
                )
                
                results = []
                for i, conversation_id in enumerate(conversation_ids):
                    try:
                        insights = await engine.get_conversation_insights(conversation_id)
                        results.append({
                            "conversation_id": conversation_id,
                            "insights": insights,
                            "status": "success"
                        })
                        
                        # Update progress
                        progress = int((i + 1) / len(conversation_ids) * 100)
                        current_task.update_state(
                            state="PROCESSING",
                            meta={
                                "total_conversations": len(conversation_ids),
                                "processed": i + 1,
                                "progress": progress,
                                "status": f"Analyzed {i + 1}/{len(conversation_ids)} conversations"
                            }
                        )
                        
                    except Exception as e:
                        logger.error(f"Error analyzing conversation {conversation_id}: {e}")
                        results.append({
                            "conversation_id": conversation_id,
                            "error": str(e),
                            "status": "error"
                        })
                
                return results
        
        # Run the async process
        results = run_async_task(analyze_conversations())
        
        # Final success state
        self.update_state(
            state="SUCCESS",
            meta={
                "total_conversations": len(conversation_ids),
                "processed": len(conversation_ids),
                "progress": 100,
                "status": "Analysis completed",
                "completed_at": datetime.utcnow().isoformat(),
                "results": results
            }
        )
        
        logger.info(f"Successfully completed batch conversation analysis task {task_id}")
        return results
        
    except Exception as e:
        logger.error(f"Error in batch conversation analysis task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

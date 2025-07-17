from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.schemas import (
    Conversation, ConversationCreate, ConversationMessage, 
    ConversationStatus, MessageSender
)
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class ConversationService:
    """Service class for conversation-related MongoDB operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.conversations
    
    async def create_conversation(self, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation"""
        try:
            conversation_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            conversation_doc = {
                "_id": conversation_id,
                "conversation_id": conversation_id,
                "customer_id": conversation_data.customer_id,
                "business_id": conversation_data.business_id,
                "product_context": conversation_data.product_context,
                "conversation_branch": conversation_data.conversation_branch.value,
                "messages": [],
                "status": ConversationStatus.ACTIVE.value,
                "created_at": now,
                "updated_at": now
            }
            
            await self.collection.insert_one(conversation_doc)
            
            return Conversation(
                conversation_id=conversation_id,
                customer_id=conversation_data.customer_id,
                business_id=conversation_data.business_id,
                product_context=conversation_data.product_context,
                conversation_branch=conversation_data.conversation_branch,
                messages=[],
                status=ConversationStatus.ACTIVE,
                created_at=now,
                updated_at=now
            )
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise
    
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        try:
            doc = await self.collection.find_one({"conversation_id": conversation_id})
            if doc:
                return self._doc_to_pydantic(doc)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            raise
    
    async def add_message(self, conversation_id: str, message: ConversationMessage) -> bool:
        """Add a message to an existing conversation"""
        try:
            message_doc = {
                "timestamp": message.timestamp,
                "sender": message.sender.value,
                "content": message.content,
                "intent": message.intent,
                "sentiment": message.sentiment
            }
            
            result = await self.collection.update_one(
                {"_id": conversation_id},
                {
                    "$push": {"messages": message_doc},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
            raise
    
    async def update_conversation_status(self, conversation_id: str, status: ConversationStatus) -> bool:
        """Update conversation status"""
        try:
            result = await self.collection.update_one(
                {"_id": conversation_id},
                {
                    "$set": {
                        "status": status.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to update conversation status {conversation_id}: {e}")
            raise
    
    async def get_conversation_history(self, conversation_id: str) -> List[ConversationMessage]:
        """Get all messages from a conversation"""
        try:
            doc = await self.collection.find_one(
                {"_id": conversation_id},
                {"messages": 1}
            )
            
            if doc and "messages" in doc:
                messages = []
                for msg_doc in doc["messages"]:
                    messages.append(ConversationMessage(
                        timestamp=msg_doc["timestamp"],
                        sender=MessageSender(msg_doc["sender"]),
                        content=msg_doc["content"],
                        intent=msg_doc.get("intent"),
                        sentiment=msg_doc.get("sentiment")
                    ))
                return messages
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get conversation history {conversation_id}: {e}")
            raise
    
    async def get_active_conversations_for_customer(self, customer_id: str) -> List[Conversation]:
        """Get all active conversations for a customer"""
        try:
            cursor = self.collection.find({
                "customer_id": customer_id,
                "status": ConversationStatus.ACTIVE.value
            })
            
            conversations = []
            async for doc in cursor:
                conversations.append(self._doc_to_pydantic(doc))
            
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get active conversations for customer {customer_id}: {e}")
            raise
    
    def _doc_to_pydantic(self, doc: Dict[str, Any]) -> Conversation:
        """Convert MongoDB document to Pydantic model"""
        messages = []
        for msg_doc in doc.get("messages", []):
            messages.append(ConversationMessage(
                timestamp=msg_doc["timestamp"],
                sender=MessageSender(msg_doc["sender"]),
                content=msg_doc["content"],
                intent=msg_doc.get("intent"),
                sentiment=msg_doc.get("sentiment")
            ))
        
        return Conversation(
            conversation_id=doc["conversation_id"],
            customer_id=doc["customer_id"],
            business_id=doc["business_id"],
            product_context=doc["product_context"],
            conversation_branch=doc["conversation_branch"],
            messages=messages,
            status=ConversationStatus(doc["status"]),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )

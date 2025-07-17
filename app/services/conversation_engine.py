from typing import List, Dict, Any, Optional
from app.services.ai_service import AzureOpenAIService
from app.services.prompt_engine import PromptEngine
from app.services.conversation_manager import ConversationManager
from app.services.product_service import ProductService
from app.services.conversation_service import ConversationService
from app.models.schemas import (
    ConversationMessage, MessageSender, ConversationStatus,
    ConversationContext, Product, ConversationBranch
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConversationEngine:
    """
    Enhanced conversation engine that orchestrates sophisticated conversation flow
    with advanced prompt engineering and conversation management
    """
    
    def __init__(
        self,
        ai_service: AzureOpenAIService,
        product_service: ProductService,
        conversation_service: ConversationService
    ):
        self.ai_service = ai_service
        self.product_service = product_service
        self.conversation_service = conversation_service
        
        # Initialize enhanced components
        self.prompt_engine = PromptEngine()
        self.conversation_manager = ConversationManager(
            ai_service=ai_service,
            prompt_engine=self.prompt_engine,
            product_service=product_service,
            conversation_service=conversation_service
        )
    
    async def process_manipulator_interaction(
        self,
        customer_id: str,
        business_id: str,
        interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhanced processing for Manipulator branch (ad interactions) with sophisticated prompts
        """
        try:
            logger.info(f"Processing Manipulator interaction for customer {customer_id}")
            
            # Extract interaction details
            interaction_type = interaction_data.get("type", "click")
            product_id = interaction_data.get("product_id")
            platform = interaction_data.get("platform", "unknown")
            
            # Prepare initial context
            initial_context = {
                "product_id": product_id,
                "interaction_type": interaction_type,
                "platform": platform,
                "interaction_timestamp": datetime.utcnow().isoformat()
            }
            
            # Start conversation with enhanced welcome protocol
            conversation_id, welcome_message = await self.conversation_manager.start_conversation(
                customer_id=customer_id,
                business_id=business_id,
                branch=ConversationBranch.MANIPULATOR,
                initial_context=initial_context,
                interaction_type=interaction_type
            )
            
            if not conversation_id:
                logger.error("Failed to create conversation")
                return {
                    "success": False,
                    "error": "Failed to initialize conversation"
                }
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "ai_response": welcome_message,
                "branch": "manipulator",
                "interaction_type": interaction_type,
                "next_action": "await_customer_response"
            }
            
        except Exception as e:
            logger.error(f"Error processing manipulator interaction: {e}")
            return {
                "success": False,
                "error": "Failed to process interaction"
            }
    
    async def process_convincer_message(
        self,
        conversation_id: str,
        customer_message: str,
        business_context: str = "We sell electronics including smartphones, laptops, headphones, and fashion items."
    ) -> str:
        """
        Process Convincer branch message (customer initiated contact)
        
        Flow:
        1. Extract keywords using keyRetriever (AI)
        2. Find matching products using tagMatcher
        3. Create conversation context
        4. Generate AI response
        5. Store response in conversation
        """
        try:
            logger.info(f"Processing convincer message for conversation {conversation_id}")
            
            # Get conversation details
            conversation = await self.conversation_service.get_conversation(conversation_id)
            if not conversation:
                logger.error(f"Conversation {conversation_id} not found")
                return "I apologize, there was an issue with the conversation."
            
            # Step 1: keyRetriever - Extract keywords from customer message
            keywords = await self.ai_service.extract_keywords(customer_message, business_context)
            logger.info(f"keyRetriever extracted: {keywords}")
            
            # Step 2: tagMatcher - Find matching products
            matching_products = []
            if keywords:
                matches = await self.product_service.search_products_by_tags(
                    keywords, 
                    threshold=0.3  # Lower threshold for better recall
                )
                
                # Convert matches to Product objects
                for match in matches:
                    matching_products.append(match["product"])
                
                logger.info(f"tagMatcher found {len(matching_products)} products")
            
            # If no products found, get all products as fallback
            if not matching_products:
                logger.info("No specific matches found, using general product selection")
                all_products = await self.product_service.get_all_products()
                matching_products = all_products[:2]  # Top 2 as fallback
            
            # Update conversation product context if this is the first message
            if not conversation.product_context and matching_products:
                # Update the conversation with found product IDs
                product_ids = [p.product_id for p in matching_products[:3]]  # Top 3
                # Note: We'd need to add an update_product_context method to conversation_service
                logger.info(f"Would update conversation product context with: {product_ids}")
            
            # Step 3: Build conversation context
            context = {
                "branch": "convincer",
                "products": [p.dict() for p in matching_products[:3]],  # Top 3 matches
                "keywords": keywords,
                "conversation_history": conversation.messages
            }
            
            # Step 4: Generate AI response
            ai_response = await self.ai_service.generate_conversation_response(
                context,
                customer_message,
                is_welcome=len([msg for msg in conversation.messages if msg.sender == MessageSender.AGENT]) == 0
            )
            
            # Step 5: Store AI response in conversation
            ai_message = ConversationMessage(
                timestamp=datetime.now(),
                sender=MessageSender.AGENT,
                content=ai_response,
                intent="product_recommendation" if matching_products else "general_inquiry"
            )
            
            await self.conversation_service.add_message(conversation_id, ai_message)
            
            logger.info(f"Convincer response generated: {ai_response[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"Convincer message processing failed: {e}")
            return "Thank you for your message! I'm here to help you find the perfect product for your needs. Could you tell me more about what you're looking for?"
    
    async def continue_conversation(
        self,
        conversation_id: str,
        customer_message: str
    ) -> str:
        """
        Continue an existing conversation with a new customer message
        """
        try:
            # Get conversation
            conversation = await self.conversation_service.get_conversation(conversation_id)
            if not conversation:
                return "I apologize, I couldn't find our conversation history."
            
            # Add customer message to conversation
            customer_msg = ConversationMessage(
                timestamp=datetime.now(),
                sender=MessageSender.CUSTOMER,
                content=customer_message,
                intent="follow_up"
            )
            
            await self.conversation_service.add_message(conversation_id, customer_msg)
            
            # Process based on conversation branch
            if conversation.conversation_branch == "manipulator":
                # For manipulator, we already have product context
                if conversation.product_context:
                    product = await self.product_service.get_product_by_id(conversation.product_context[0])
                    context = {
                        "branch": "manipulator",
                        "products": [product.dict()] if product else [],
                        "conversation_history": conversation.messages + [customer_msg]
                    }
                    
                    ai_response = await self.ai_service.generate_conversation_response(
                        context, customer_message, is_welcome=False
                    )
                else:
                    ai_response = "Let me help you with that! What specific information would you like to know?"
            else:
                # For convincer, re-analyze the message for new products if needed
                ai_response = await self.process_convincer_message(
                    conversation_id, customer_message
                )
                return ai_response  # Already stored in process_convincer_message
            
            # Store AI response
            ai_message = ConversationMessage(
                timestamp=datetime.now(),
                sender=MessageSender.AGENT,
                content=ai_response,
                intent="follow_up_response"
            )
            
            await self.conversation_service.add_message(conversation_id, ai_message)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Continue conversation failed: {e}")
            return "I appreciate your message. Could you please rephrase your question so I can better assist you?"

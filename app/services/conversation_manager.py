"""
Enhanced Conversation Manager for ManipulatorAI
Integrates sophisticated prompt engineering with conversation state management
"""

from typing import List, Dict, Any, Optional, Tuple
from app.services.ai_service import AzureOpenAIService
from app.services.prompt_engine import PromptEngine
from app.services.product_service import ProductService
from app.services.conversation_service import ConversationService
from app.models.schemas import (
    ConversationMessage, MessageSender, ConversationStatus,
    ConversationBranch, Product, ConversationContext
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Enhanced conversation manager that combines AI services with sophisticated prompt engineering
    for natural, persuasive customer conversations
    """
    
    def __init__(
        self,
        ai_service: AzureOpenAIService,
        prompt_engine: PromptEngine,
        product_service: ProductService,
        conversation_service: ConversationService
    ):
        self.ai_service = ai_service
        self.prompt_engine = prompt_engine
        self.product_service = product_service
        self.conversation_service = conversation_service
        
        # Conversation state tracking
        self.conversation_states = {}
        
        # Performance tracking
        self.conversation_metrics = {
            "total_conversations": 0,
            "qualified_leads": 0,
            "uninterested_customers": 0,
            "cross_product_recommendations": 0,
            "average_message_count": 0
        }
    
    async def start_conversation(
        self,
        customer_id: str,
        business_id: str,
        branch: ConversationBranch,
        initial_context: Dict[str, Any],
        interaction_type: str = "general"
    ) -> Tuple[str, str]:
        """
        Start a new conversation with welcome protocol
        Returns (conversation_id, welcome_message)
        """
        try:
            logger.info(f"Starting {branch.value} conversation for customer {customer_id}")
            
            # Get relevant products based on context
            products = await self._get_relevant_products(initial_context, branch)
            
            # Create conversation record
            from app.models.schemas import ConversationCreate
            
            # Convert initial_context dict to product_context list of strings
            product_context_list = []
            if initial_context:
                # Extract meaningful strings from the context
                if 'initial_message' in initial_context:
                    product_context_list.append(f"message: {initial_context['initial_message']}")
                if 'product_id' in initial_context:
                    product_context_list.append(f"product_id: {initial_context['product_id']}")
                if 'source' in initial_context:
                    product_context_list.append(f"source: {initial_context['source']}")
                # Add any keywords if present
                if 'keywords' in initial_context:
                    keywords = initial_context['keywords']
                    if isinstance(keywords, list):
                        product_context_list.extend([f"keyword: {kw}" for kw in keywords])
            
            conversation_data = ConversationCreate(
                customer_id=customer_id,
                business_id=business_id,
                conversation_branch=branch,
                product_context=product_context_list
            )
            conversation = await self.conversation_service.create_conversation(conversation_data)
            conversation_id = conversation.conversation_id
            
            # Generate welcome prompt
            welcome_prompt = self.prompt_engine.generate_welcome_prompt(
                branch=branch,
                products=products,
                customer_context=initial_context,
                interaction_type=interaction_type
            )
            
            # Generate AI welcome response
            welcome_message = await self.ai_service.generate_conversation_response(
                conversation_context={
                    "branch": branch.value,
                    "products": [p.dict() for p in products],
                    "customer_context": initial_context,
                    "conversation_history": []
                },
                customer_message="",
                is_welcome=True
            )
            
            # Store welcome message
            await self.conversation_service.add_message(
                conversation_id=conversation_id,
                sender=MessageSender.AGENT,
                content=welcome_message,
                metadata={
                    "message_type": "welcome",
                    "branch": branch.value,
                    "products_count": len(products)
                }
            )
            
            # Initialize conversation state
            self.conversation_states[conversation_id] = {
                "status": ConversationStatus.ACTIVE,
                "message_count": 1,
                "products_discussed": [p.product_id for p in products],
                "customer_interest_level": "initial",
                "last_interaction": datetime.utcnow()
            }
            
            self.conversation_metrics["total_conversations"] += 1
            
            return conversation_id, welcome_message
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            return None, "Hello! How can I help you today?"
    
    async def process_customer_message(
        self,
        conversation_id: str,
        customer_message: str,
        customer_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, ConversationStatus]:
        """
        Process customer message and generate appropriate response
        Returns (ai_response, conversation_status)
        """
        try:
            logger.info(f"Processing message for conversation {conversation_id}")
            
            # Get conversation context
            conversation = await self.conversation_service.get_conversation(conversation_id)
            if not conversation:
                logger.error(f"Conversation {conversation_id} not found")
                return "I'm sorry, I couldn't find our conversation. Could you please start over?", ConversationStatus.ACTIVE
            
            # Get conversation history
            history = await self.conversation_service.get_conversation_history(conversation_id)
            
            # Store customer message
            await self.conversation_service.add_message(
                conversation_id=conversation_id,
                sender=MessageSender.CUSTOMER,
                content=customer_message,
                metadata={"timestamp": datetime.utcnow().isoformat()}
            )
            
            # Analyze customer sentiment and intent
            customer_analysis = await self._analyze_customer_message(customer_message, history)
            
            # Update conversation state
            current_state = self.conversation_states.get(conversation_id, {})
            current_state.update({
                "message_count": current_state.get("message_count", 0) + 1,
                "customer_interest_level": customer_analysis["interest_level"],
                "last_interaction": datetime.utcnow()
            })
            
            # Determine conversation status and strategy
            conversation_status = self._determine_conversation_status(customer_analysis, current_state)
            current_state["status"] = conversation_status
            
            # Get relevant products
            products = await self._get_products_for_conversation(conversation, customer_message, customer_analysis)
            
            # Handle different conversation scenarios
            if conversation_status == ConversationStatus.UNINTERESTED:
                response = await self._handle_uninterested_customer(
                    conversation, customer_message, products, history, customer_context
                )
            elif customer_analysis.get("needs_cross_recommendation", False):
                response = await self._handle_cross_product_recommendation(
                    conversation, customer_message, products, history
                )
            else:
                response = await self._handle_standard_conversation(
                    conversation, customer_message, products, history, customer_context, conversation_status
                )
            
            # Store AI response
            await self.conversation_service.add_message(
                conversation_id=conversation_id,
                sender=MessageSender.AGENT,
                content=response,
                metadata={
                    "conversation_status": conversation_status.value,
                    "customer_interest": customer_analysis["interest_level"],
                    "products_count": len(products),
                    "strategy": customer_analysis.get("strategy", "standard")
                }
            )
            
            # Update conversation state
            self.conversation_states[conversation_id] = current_state
            
            # Check if conversation should conclude
            if self._should_conclude_conversation(current_state, customer_analysis):
                await self._conclude_conversation(conversation_id, conversation_status, products)
            
            return response, conversation_status
            
        except Exception as e:
            logger.error(f"Error processing customer message: {e}")
            return "I apologize for the confusion. Could you please repeat that?", ConversationStatus.ACTIVE
    
    async def _get_relevant_products(
        self,
        context: Dict[str, Any],
        branch: ConversationBranch,
        limit: int = 3
    ) -> List[Product]:
        """Get products relevant to the conversation context"""
        try:
            if branch == ConversationBranch.MANIPULATOR:
                # For manipulator branch, try to get specific product from context
                product_id = context.get("product_id")
                if product_id:
                    product = await self.product_service.get_product_by_id(product_id)
                    if product:
                        return [product]
            
            # For convincer branch or when no specific product, get products based on keywords
            keywords = context.get("keywords", [])
            if keywords:
                matches = await self.product_service.search_products_by_keywords(keywords, threshold=0.3)
                return [match["product"] for match in matches[:limit]]
            
            # Fallback: get recent products
            return await self.product_service.get_all_products()
            
        except Exception as e:
            logger.error(f"Error getting relevant products: {e}")
            return []
    
    async def _analyze_customer_message(
        self,
        message: str,
        history: List[ConversationMessage]
    ) -> Dict[str, Any]:
        """Analyze customer message for sentiment, intent, and interest level"""
        try:
            # Use AI to analyze customer sentiment and intent
            analysis_prompt = f"""Analyze this customer message for sentiment and intent:

Message: "{message}"

Conversation context: {len(history)} previous messages

Provide analysis in JSON format:
{{
    "interest_level": "high|medium|low|declining",
    "sentiment": "positive|neutral|negative",
    "intent": "information|purchase|comparison|objection|leaving",
    "needs_cross_recommendation": true/false,
    "key_concerns": ["concern1", "concern2"],
    "strategy": "engage|persuade|recover|conclude"
}}"""

            analysis_response = await self.ai_service.generate_completion(
                prompt=analysis_prompt,
                max_tokens=200,
                temperature=0.3
            )
            
            # Parse JSON response (with fallback)
            try:
                import json
                analysis = json.loads(analysis_response)
            except:
                # Fallback analysis based on keywords
                analysis = self._fallback_message_analysis(message)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing customer message: {e}")
            return self._fallback_message_analysis(message)
    
    def _fallback_message_analysis(self, message: str) -> Dict[str, Any]:
        """Fallback message analysis when AI analysis fails"""
        message_lower = message.lower()
        
        # Simple keyword-based analysis
        negative_keywords = ["no", "not interested", "don't want", "too expensive", "bye", "goodbye"]
        positive_keywords = ["yes", "interested", "tell me more", "how much", "buy", "purchase"]
        question_keywords = ["what", "how", "when", "where", "which", "?"]
        
        if any(word in message_lower for word in negative_keywords):
            interest_level = "declining"
            sentiment = "negative"
            intent = "objection"
        elif any(word in message_lower for word in positive_keywords):
            interest_level = "high"
            sentiment = "positive"
            intent = "purchase"
        elif any(word in message_lower for word in question_keywords):
            interest_level = "medium"
            sentiment = "neutral"
            intent = "information"
        else:
            interest_level = "medium"
            sentiment = "neutral"
            intent = "information"
        
        return {
            "interest_level": interest_level,
            "sentiment": sentiment,
            "intent": intent,
            "needs_cross_recommendation": False,
            "key_concerns": [],
            "strategy": "engage" if interest_level != "declining" else "recover"
        }
    
    def _determine_conversation_status(
        self,
        customer_analysis: Dict[str, Any],
        conversation_state: Dict[str, Any]
    ) -> ConversationStatus:
        """Determine the current conversation status"""
        interest_level = customer_analysis.get("interest_level", "medium")
        intent = customer_analysis.get("intent", "information")
        message_count = conversation_state.get("message_count", 0)
        
        if intent == "purchase" and interest_level in ["high", "medium"]:
            return ConversationStatus.QUALIFIED
        elif interest_level == "declining" or intent in ["objection", "leaving"]:
            return ConversationStatus.UNINTERESTED
        elif message_count > 10 and interest_level == "low":
            return ConversationStatus.UNINTERESTED
        else:
            return ConversationStatus.ACTIVE
    
    async def _get_products_for_conversation(
        self,
        conversation: Dict[str, Any],
        customer_message: str,
        customer_analysis: Dict[str, Any]
    ) -> List[Product]:
        """Get products relevant to current conversation context"""
        try:
            # Extract keywords from current message
            keywords = await self.ai_service.extract_keywords(
                customer_message,
                "We sell electronics, fashion, and lifestyle products"
            )
            
            if keywords:
                matches = await self.product_service.search_products_by_keywords(keywords, threshold=0.3)
                if matches:
                    return [match["product"] for match in matches[:3]]
            
            # Fallback to conversation's initial products
            initial_context = conversation.get("initial_context", {})
            return await self._get_relevant_products(initial_context, ConversationBranch(conversation.get("branch", "convincer")))
            
        except Exception as e:
            logger.error(f"Error getting products for conversation: {e}")
            return []
    
    async def _handle_standard_conversation(
        self,
        conversation: Dict[str, Any],
        customer_message: str,
        products: List[Product],
        history: List[ConversationMessage],
        customer_context: Optional[Dict[str, Any]],
        status: ConversationStatus
    ) -> str:
        """Handle standard conversation flow"""
        try:
            branch = ConversationBranch(conversation.get("branch", "convincer"))
            
            # Generate conversation prompt
            conversation_prompt = self.prompt_engine.generate_conversation_prompt(
                branch=branch,
                customer_message=customer_message,
                products=products,
                conversation_history=[msg.dict() for msg in history[-5:]],  # Last 5 messages
                customer_context=customer_context or {},
                conversation_status=status
            )
            
            # Generate AI response
            response = await self.ai_service.generate_conversation_response(
                conversation_context={
                    "branch": branch.value,
                    "products": [p.dict() for p in products],
                    "conversation_history": [msg.dict() for msg in history[-5:]],
                    "customer_context": customer_context or {}
                },
                customer_message=customer_message,
                is_welcome=False
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling standard conversation: {e}")
            return "I understand what you're saying. Let me help you find the best solution for your needs."
    
    async def _handle_uninterested_customer(
        self,
        conversation: Dict[str, Any],
        customer_message: str,
        products: List[Product],
        history: List[ConversationMessage],
        customer_context: Optional[Dict[str, Any]]
    ) -> str:
        """Handle uninterested customers with recovery strategies"""
        try:
            # Try cross-product recommendation first
            alternative_products = await self._get_alternative_products(products)
            
            if alternative_products:
                self.conversation_metrics["cross_product_recommendations"] += 1
                return await self._handle_cross_product_recommendation(
                    conversation, customer_message, alternative_products, history
                )
            
            # Generate recovery prompt
            recovery_prompt = self.prompt_engine.generate_conversation_prompt(
                branch=ConversationBranch(conversation.get("branch", "convincer")),
                customer_message=customer_message,
                products=products,
                conversation_history=[msg.dict() for msg in history[-3:]],
                customer_context=customer_context or {},
                conversation_status=ConversationStatus.UNINTERESTED
            )
            
            response = await self.ai_service.generate_conversation_response(
                conversation_context={
                    "branch": conversation.get("branch", "convincer"),
                    "products": [p.dict() for p in products],
                    "conversation_history": [msg.dict() for msg in history[-3:]],
                    "recovery_mode": True
                },
                customer_message=customer_message,
                is_welcome=False
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling uninterested customer: {e}")
            return "I understand. Thank you for your time, and please feel free to reach out if you have any questions in the future."
    
    async def _handle_cross_product_recommendation(
        self,
        conversation: Dict[str, Any],
        customer_message: str,
        alternative_products: List[Product],
        history: List[ConversationMessage]
    ) -> str:
        """Handle cross-product recommendations"""
        try:
            original_products = await self._get_original_products(conversation)
            
            cross_product_prompt = self.prompt_engine.generate_cross_product_recommendation_prompt(
                original_products=original_products,
                alternative_products=alternative_products,
                customer_message=customer_message,
                conversation_history=[msg.dict() for msg in history[-3:]]
            )
            
            response = await self.ai_service.generate_conversation_response(
                conversation_context={
                    "branch": conversation.get("branch", "convincer"),
                    "original_products": [p.dict() for p in original_products],
                    "alternative_products": [p.dict() for p in alternative_products],
                    "conversation_history": [msg.dict() for msg in history[-3:]],
                    "cross_recommendation": True
                },
                customer_message=customer_message,
                is_welcome=False
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling cross-product recommendation: {e}")
            return "Based on what you've mentioned, you might be interested in some of our other products that could be a better fit for your needs."
    
    async def _get_alternative_products(self, current_products: List[Product]) -> List[Product]:
        """Get alternative products for cross-recommendations"""
        try:
            if not current_products:
                return []
            
            # Get products from different categories
            current_categories = set()
            for product in current_products:
                if hasattr(product, 'product_attributes') and 'category' in product.product_attributes:
                    current_categories.add(product.product_attributes['category'])
            
            # Search for products in different categories
            alternative_keywords = ["alternative", "different", "other"]
            matches = await self.product_service.search_products_by_keywords(alternative_keywords, threshold=0.1)
            
            # Filter out products from same categories
            alternatives = []
            for match in matches:
                product = match["product"]
                if hasattr(product, 'product_attributes') and 'category' in product.product_attributes:
                    if product.product_attributes['category'] not in current_categories:
                        alternatives.append(product)
                        if len(alternatives) >= 3:
                            break
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Error getting alternative products: {e}")
            return []
    
    async def _get_original_products(self, conversation: Dict[str, Any]) -> List[Product]:
        """Get the original products discussed in conversation"""
        try:
            initial_context = conversation.get("initial_context", {})
            return await self._get_relevant_products(
                initial_context,
                ConversationBranch(conversation.get("branch", "convincer"))
            )
        except Exception as e:
            logger.error(f"Error getting original products: {e}")
            return []
    
    def _should_conclude_conversation(
        self,
        conversation_state: Dict[str, Any],
        customer_analysis: Dict[str, Any]
    ) -> bool:
        """Determine if conversation should be concluded"""
        status = conversation_state.get("status")
        message_count = conversation_state.get("message_count", 0)
        intent = customer_analysis.get("intent", "information")
        
        return (
            status == ConversationStatus.QUALIFIED or
            (status == ConversationStatus.UNINTERESTED and message_count > 3) or
            intent == "leaving" or
            message_count > 15
        )
    
    async def _conclude_conversation(
        self,
        conversation_id: str,
        final_status: ConversationStatus,
        products_discussed: List[Product]
    ) -> None:
        """Conclude conversation with appropriate closing message"""
        try:
            # Get conversation history for context
            history = await self.conversation_service.get_conversation_history(conversation_id)
            
            # Generate conclusion prompt
            conclusion_prompt = self.prompt_engine.generate_conclusion_prompt(
                conversation_history=[msg.dict() for msg in history[-5:]],
                final_status=final_status,
                products_discussed=products_discussed
            )
            
            # Generate conclusion message
            conclusion_message = await self.ai_service.generate_conversation_response(
                conversation_context={
                    "final_status": final_status.value,
                    "products_discussed": [p.dict() for p in products_discussed],
                    "conversation_history": [msg.dict() for msg in history[-3:]],
                    "conclusion": True
                },
                customer_message="",
                is_welcome=False
            )
            
            # Store conclusion message
            await self.conversation_service.add_message(
                conversation_id=conversation_id,
                sender=MessageSender.AGENT,
                content=conclusion_message,
                metadata={
                    "message_type": "conclusion",
                    "final_status": final_status.value,
                    "conclusion_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Update conversation status
            await self.conversation_service.update_conversation_status(conversation_id, final_status)
            
            # Update metrics
            if final_status == ConversationStatus.QUALIFIED:
                self.conversation_metrics["qualified_leads"] += 1
            elif final_status == ConversationStatus.UNINTERESTED:
                self.conversation_metrics["uninterested_customers"] += 1
            
            # Update average message count
            state = self.conversation_states.get(conversation_id, {})
            message_count = state.get("message_count", 0)
            total_conversations = self.conversation_metrics["total_conversations"]
            current_avg = self.conversation_metrics["average_message_count"]
            self.conversation_metrics["average_message_count"] = (
                (current_avg * (total_conversations - 1) + message_count) / total_conversations
            )
            
            logger.info(f"Conversation {conversation_id} concluded with status: {final_status.value}")
            
        except Exception as e:
            logger.error(f"Error concluding conversation: {e}")
    
    def get_conversation_metrics(self) -> Dict[str, Any]:
        """Get conversation performance metrics"""
        metrics = self.conversation_metrics.copy()
        
        if metrics["total_conversations"] > 0:
            metrics["qualification_rate"] = metrics["qualified_leads"] / metrics["total_conversations"]
            metrics["engagement_rate"] = 1 - (metrics["uninterested_customers"] / metrics["total_conversations"])
        else:
            metrics["qualification_rate"] = 0
            metrics["engagement_rate"] = 0
        
        return metrics
    
    def get_active_conversations_count(self) -> int:
        """Get count of currently active conversations"""
        return len([
            state for state in self.conversation_states.values()
            if state.get("status") == ConversationStatus.ACTIVE
        ])

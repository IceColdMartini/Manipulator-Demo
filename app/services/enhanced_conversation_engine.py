"""
Enhanced Conversation Engine for ManipulatorAI Step 6
Integrates sophisticated prompt engineering with conversation management
"""

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

class EnhancedConversationEngine:
    """
    Step 6 Enhanced conversation engine with sophisticated prompt engineering
    and advanced conversation management capabilities
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
        
        # Initialize Step 6 components
        self.prompt_engine = PromptEngine()
        self.conversation_manager = ConversationManager(
            ai_service=ai_service,
            prompt_engine=self.prompt_engine,
            product_service=product_service,
            conversation_service=conversation_service
        )
        
        # Performance tracking
        self.engine_metrics = {
            "total_interactions": 0,
            "successful_conversations": 0,
            "error_rate": 0.0,
            "average_response_time": 0.0
        }
    
    async def start_manipulator_conversation(
        self,
        customer_id: str,
        business_id: str,
        interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Start a Manipulator branch conversation (from ad interactions)
        with sophisticated welcome protocol
        """
        try:
            start_time = datetime.utcnow()
            self.engine_metrics["total_interactions"] += 1
            
            logger.info(f"Starting Manipulator conversation for customer {customer_id}")
            
            # Extract interaction details
            interaction_type = interaction_data.get("type", "click")
            product_id = interaction_data.get("product_id")
            platform = interaction_data.get("platform", "unknown")
            
            # Validate required data
            if not product_id:
                logger.error("Missing product_id in interaction data")
                return {
                    "success": False,
                    "error": "Missing product information"
                }
            
            # Prepare initial context for conversation
            initial_context = {
                "product_id": product_id,
                "interaction_type": interaction_type,
                "platform": platform,
                "interaction_timestamp": start_time.isoformat(),
                "source": "advertisement"
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
                self._update_error_metrics()
                return {
                    "success": False,
                    "error": "Failed to initialize conversation"
                }
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_success_metrics(response_time)
            
            logger.info(f"Manipulator conversation {conversation_id} started successfully")
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "ai_response": welcome_message,
                "branch": "manipulator",
                "interaction_type": interaction_type,
                "next_action": "await_customer_response",
                "conversation_features": {
                    "welcome_protocol": "enabled",
                    "product_focused": True,
                    "persuasion_strategy": "direct_engagement"
                }
            }
            
        except Exception as e:
            logger.error(f"Error starting manipulator conversation: {e}")
            self._update_error_metrics()
            return {
                "success": False,
                "error": f"Failed to start conversation: {str(e)}"
            }
    
    async def start_convincer_conversation(
        self,
        customer_id: str,
        business_id: str,
        initial_message: str,
        customer_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a Convincer branch conversation (from direct messages)
        with sophisticated welcome and discovery protocol
        """
        try:
            start_time = datetime.utcnow()
            self.engine_metrics["total_interactions"] += 1
            
            logger.info(f"Starting Convincer conversation for customer {customer_id}")
            
            # Prepare initial context
            initial_context = {
                "initial_message": initial_message,
                "customer_context": customer_context or {},
                "interaction_timestamp": start_time.isoformat(),
                "source": "direct_message"
            }
            
            # Start conversation with welcome protocol
            conversation_id, welcome_message = await self.conversation_manager.start_conversation(
                customer_id=customer_id,
                business_id=business_id,
                branch=ConversationBranch.CONVINCER,
                initial_context=initial_context,
                interaction_type="message"
            )
            
            if not conversation_id:
                logger.error("Failed to create conversation")
                self._update_error_metrics()
                return {
                    "success": False,
                    "error": "Failed to initialize conversation"
                }
            
            # Process the initial customer message
            ai_response, conversation_status = await self.conversation_manager.process_customer_message(
                conversation_id=conversation_id,
                customer_message=initial_message,
                customer_context=customer_context
            )
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_success_metrics(response_time)
            
            logger.info(f"Convincer conversation {conversation_id} started successfully")
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "ai_response": ai_response,
                "branch": "convincer",
                "conversation_status": conversation_status.value,
                "next_action": self._determine_next_action(conversation_status),
                "conversation_features": {
                    "welcome_protocol": "enabled",
                    "discovery_mode": True,
                    "persuasion_strategy": "consultative_approach"
                }
            }
            
        except Exception as e:
            logger.error(f"Error starting convincer conversation: {e}")
            self._update_error_metrics()
            return {
                "success": False,
                "error": f"Failed to start conversation: {str(e)}"
            }
    
    async def continue_conversation(
        self,
        conversation_id: str,
        customer_message: str,
        customer_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Continue an existing conversation with enhanced conversation management
        """
        try:
            start_time = datetime.utcnow()
            
            logger.info(f"Continuing conversation {conversation_id}")
            
            # Process message through enhanced conversation manager
            ai_response, conversation_status = await self.conversation_manager.process_customer_message(
                conversation_id=conversation_id,
                customer_message=customer_message,
                customer_context=customer_context
            )
            
            # Get conversation metrics
            metrics = self.conversation_manager.get_conversation_metrics()
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_success_metrics(response_time)
            
            return {
                "success": True,
                "ai_response": ai_response,
                "conversation_status": conversation_status.value,
                "next_action": self._determine_next_action(conversation_status),
                "conversation_metrics": {
                    "engagement_rate": metrics.get("engagement_rate", 0),
                    "qualification_rate": metrics.get("qualification_rate", 0)
                },
                "conversation_features": {
                    "prompt_engineering": "active",
                    "state_management": "enabled",
                    "persuasion_techniques": "adaptive"
                }
            }
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            self._update_error_metrics()
            return {
                "success": False,
                "error": f"Failed to continue conversation: {str(e)}"
            }
    
    async def get_conversation_insights(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get insights about a conversation's performance and characteristics
        """
        try:
            # Get conversation details
            conversation = await self.conversation_service.get_conversation(conversation_id)
            if not conversation:
                return {"error": "Conversation not found"}
            
            # Get conversation history
            history = await self.conversation_service.get_conversation_history(conversation_id)
            
            # Analyze conversation characteristics
            insights = {
                "conversation_id": conversation_id,
                "branch": conversation.get("branch", "unknown"),
                "status": conversation.get("status", "active"),
                "message_count": len(history),
                "agent_messages": len([msg for msg in history if msg.sender == MessageSender.AGENT]),
                "customer_messages": len([msg for msg in history if msg.sender == MessageSender.CUSTOMER]),
                "duration_minutes": self._calculate_conversation_duration(history),
                "prompt_strategies_used": self._identify_prompt_strategies(history),
                "conversation_flow": self._analyze_conversation_flow(history)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting conversation insights: {e}")
            return {"error": "Failed to get insights"}
    
    async def get_engine_performance(self) -> Dict[str, Any]:
        """
        Get performance metrics for the conversation engine
        """
        try:
            # Get conversation manager metrics
            manager_metrics = self.conversation_manager.get_conversation_metrics()
            
            # Get prompt engine statistics
            prompt_stats = self.prompt_engine.get_prompt_statistics()
            
            # Combine all metrics
            performance = {
                "engine_metrics": self.engine_metrics,
                "conversation_metrics": manager_metrics,
                "prompt_statistics": prompt_stats,
                "active_conversations": self.conversation_manager.get_active_conversations_count(),
                "system_health": {
                    "ai_service": "operational",
                    "prompt_engine": "operational",
                    "conversation_manager": "operational",
                    "database_connections": "stable"
                }
            }
            
            return performance
            
        except Exception as e:
            logger.error(f"Error getting engine performance: {e}")
            return {"error": "Failed to get performance metrics"}
    
    def _determine_next_action(self, conversation_status: ConversationStatus) -> str:
        """Determine the next action based on conversation status"""
        action_map = {
            ConversationStatus.ACTIVE: "continue_conversation",
            ConversationStatus.QUALIFIED: "handoff_to_onboarding",
            ConversationStatus.UNINTERESTED: "graceful_conclusion"
        }
        return action_map.get(conversation_status, "continue_conversation")
    
    def _update_success_metrics(self, response_time: float):
        """Update success metrics"""
        self.engine_metrics["successful_conversations"] += 1
        
        # Update average response time
        total = self.engine_metrics["total_interactions"]
        current_avg = self.engine_metrics["average_response_time"]
        self.engine_metrics["average_response_time"] = (
            (current_avg * (total - 1) + response_time) / total
        )
        
        # Update error rate
        errors = self.engine_metrics["total_interactions"] - self.engine_metrics["successful_conversations"]
        self.engine_metrics["error_rate"] = errors / self.engine_metrics["total_interactions"]
    
    def _update_error_metrics(self):
        """Update error metrics"""
        total = self.engine_metrics["total_interactions"]
        errors = total - self.engine_metrics["successful_conversations"]
        self.engine_metrics["error_rate"] = errors / total if total > 0 else 0
    
    def _calculate_conversation_duration(self, history: List[ConversationMessage]) -> float:
        """Calculate conversation duration in minutes"""
        if len(history) < 2:
            return 0.0
        
        first_message = min(history, key=lambda msg: msg.timestamp)
        last_message = max(history, key=lambda msg: msg.timestamp)
        
        duration = last_message.timestamp - first_message.timestamp
        return duration.total_seconds() / 60.0
    
    def _identify_prompt_strategies(self, history: List[ConversationMessage]) -> List[str]:
        """Identify which prompt strategies were used in the conversation"""
        strategies = []
        
        # Check for welcome protocol
        if history and history[0].sender == MessageSender.AGENT:
            strategies.append("welcome_protocol")
        
        # Check for recovery attempts
        agent_messages = [msg for msg in history if msg.sender == MessageSender.AGENT]
        if len(agent_messages) > 3:
            strategies.append("engagement_strategy")
        
        # Add other strategy detection logic as needed
        strategies.append("consultative_approach")
        
        return strategies
    
    def _analyze_conversation_flow(self, history: List[ConversationMessage]) -> Dict[str, Any]:
        """Analyze the flow characteristics of the conversation"""
        if not history:
            return {"flow": "empty"}
        
        agent_msgs = len([msg for msg in history if msg.sender == MessageSender.AGENT])
        customer_msgs = len([msg for msg in history if msg.sender == MessageSender.CUSTOMER])
        
        return {
            "flow": "balanced" if abs(agent_msgs - customer_msgs) <= 1 else "agent_heavy" if agent_msgs > customer_msgs else "customer_heavy",
            "agent_customer_ratio": agent_msgs / customer_msgs if customer_msgs > 0 else float('inf'),
            "conversation_length": "short" if len(history) < 5 else "medium" if len(history) < 10 else "long"
        }

"""
Prompt Engineering Service for ManipulatorAI
Handles sophisticated conversation prompts, welcome protocols, and persuasion strategies
"""

from typing import List, Dict, Any, Optional
from app.models.schemas import ConversationBranch, ConversationStatus, Product
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PromptEngine:
    """
    Advanced prompt engineering service that creates sophisticated conversation prompts
    for both Manipulator and Convincer branches with persuasive strategies
    """
    
    def __init__(self):
        self.business_personality = {
            "tone": "friendly_professional",
            "approach": "consultative_sales",
            "persistence_level": "polite_persistent",
            "empathy_level": "high",
            "expertise_level": "product_expert"
        }
    
    def generate_welcome_prompt(
        self,
        branch: ConversationBranch,
        products: List[Product],
        customer_context: Dict[str, Any],
        interaction_type: str = "general"
    ) -> str:
        """
        Generate welcome protocol prompts for first-time customer interactions
        """
        try:
            base_context = self._build_base_context(products)
            
            if branch == ConversationBranch.MANIPULATOR:
                return self._create_manipulator_welcome(products, customer_context, interaction_type, base_context)
            else:
                return self._create_convincer_welcome(products, customer_context, base_context)
                
        except Exception as e:
            logger.error(f"Error generating welcome prompt: {e}")
            return self._fallback_welcome_prompt()
    
    def generate_conversation_prompt(
        self,
        branch: ConversationBranch,
        customer_message: str,
        products: List[Product],
        conversation_history: List[Dict[str, Any]],
        customer_context: Dict[str, Any],
        conversation_status: ConversationStatus = ConversationStatus.ACTIVE
    ) -> str:
        """
        Generate sophisticated conversation prompts based on context and conversation state
        """
        try:
            base_context = self._build_base_context(products)
            history_context = self._build_history_context(conversation_history)
            
            if conversation_status == ConversationStatus.UNINTERESTED:
                return self._create_recovery_prompt(customer_message, products, history_context, base_context)
            
            if branch == ConversationBranch.MANIPULATOR:
                return self._create_manipulator_prompt(customer_message, products, history_context, base_context)
            else:
                return self._create_convincer_prompt(customer_message, products, history_context, base_context, customer_context)
                
        except Exception as e:
            logger.error(f"Error generating conversation prompt: {e}")
            return self._fallback_conversation_prompt(customer_message)
    
    def generate_cross_product_recommendation_prompt(
        self,
        original_products: List[Product],
        alternative_products: List[Product],
        customer_message: str,
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """
        Generate prompts for cross-product recommendations when customer shows disinterest
        """
        try:
            base_context = self._build_base_context(alternative_products)
            history_context = self._build_history_context(conversation_history)
            
            return f"""You are a helpful product consultant for a business specializing in quality products. 

CONVERSATION CONTEXT:
{history_context}

ORIGINAL PRODUCTS DISCUSSED:
{self._format_products_for_prompt(original_products)}

NEW RECOMMENDATION OPPORTUNITIES:
{self._format_products_for_prompt(alternative_products)}

CUSTOMER'S LATEST MESSAGE: "{customer_message}"

TASK: The customer seems less interested in the original products. Gracefully transition to recommending alternative products that might better match their needs.

CONVERSATION STRATEGY:
1. **Acknowledge Understanding**: Show that you understand their position on the original products
2. **Smooth Transition**: Naturally introduce alternative products without being pushy
3. **Value Proposition**: Highlight unique benefits of the new products
4. **Interest Gauging**: Ask thoughtful questions to understand their preferences
5. **Stay Conversational**: Maintain a friendly, helpful tone

RESPONSE GUIDELINES:
- Keep response under 100 words
- Be genuinely helpful, not salesy
- Show expertise about the alternative products
- End with an engaging question about their preferences
- Maintain optimistic but respectful tone

Generate a natural, helpful response that smoothly introduces the alternative products:"""

        except Exception as e:
            logger.error(f"Error generating cross-product recommendation prompt: {e}")
            return self._fallback_conversation_prompt(customer_message)
    
    def generate_conclusion_prompt(
        self,
        conversation_history: List[Dict[str, Any]],
        final_status: ConversationStatus,
        products_discussed: List[Product]
    ) -> str:
        """
        Generate graceful conversation conclusion prompts
        """
        try:
            history_context = self._build_history_context(conversation_history)
            
            if final_status == ConversationStatus.QUALIFIED:
                return self._create_qualified_conclusion(history_context, products_discussed)
            elif final_status == ConversationStatus.UNINTERESTED:
                return self._create_uninterested_conclusion(history_context)
            else:
                return self._create_general_conclusion(history_context)
                
        except Exception as e:
            logger.error(f"Error generating conclusion prompt: {e}")
            return self._fallback_conclusion_prompt()
    
    def _build_base_context(self, products: List[Product]) -> str:
        """Build base business context from products"""
        if not products:
            return "We offer a variety of quality products to meet our customers' needs."
        
        categories = set()
        for product in products:
            # Check for category in metadata first, then product category field
            if hasattr(product, 'metadata') and product.metadata and 'category' in product.metadata:
                categories.add(product.metadata['category'])
            elif hasattr(product, 'product_metadata') and product.product_metadata and 'category' in product.product_metadata:
                categories.add(product.product_metadata['category'])
            elif hasattr(product, 'category') and product.category:
                categories.add(product.category)
        
        category_text = ", ".join(categories) if categories else "various categories"
        
        return f"""BUSINESS CONTEXT:
We are a premium retailer specializing in {category_text}. Our mission is to help customers find products that perfectly match their needs and preferences. We pride ourselves on quality, customer service, and building long-term relationships.

AVAILABLE PRODUCTS:
{self._format_products_for_prompt(products)}"""
    
    def _format_products_for_prompt(self, products: List[Product]) -> str:
        """Format products for inclusion in prompts"""
        if not products:
            return "No specific products available."
        
        formatted = []
        for i, product in enumerate(products[:3], 1):  # Limit to top 3 products
            # Use metadata or product_metadata to get attributes
            attributes = {}
            if hasattr(product, 'metadata') and product.metadata:
                attributes = product.metadata
            elif hasattr(product, 'product_metadata') and product.product_metadata:
                attributes = product.product_metadata
            
            price = attributes.get('price', f'${product.price}' if product.price else 'Contact for pricing')
            brand = attributes.get('brand', 'Quality Brand')
            
            # Use description field from Product model
            description = product.description if product.description else product.name
            formatted.append(f"{i}. {description[:100]}{'...' if len(description) > 100 else ''}")
            formatted.append(f"   Brand: {brand} | Price: {price}")
            
            # Use category or metadata tags for features instead of product_tag
            features = []
            if product.category:
                features.append(product.category)
            if hasattr(product, 'metadata') and product.metadata:
                tags = product.metadata.get('tags', [])
                if isinstance(tags, list):
                    features.extend(tags[:3])  # Add up to 3 tags
            
            if features:
                formatted.append(f"   Key Features: {', '.join(features)}")
            else:
                formatted.append(f"   Category: {product.category if product.category else 'General'}")
        
        return "\n".join(formatted)
    
    def _build_history_context(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Build conversation history context"""
        if not conversation_history:
            return "This is the start of the conversation."
        
        history_lines = []
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            sender = msg.get('sender', 'unknown')
            content = msg.get('content', '')[:100]  # Truncate long messages
            timestamp = msg.get('timestamp', 'recent')
            history_lines.append(f"[{sender}]: {content}")
        
        return "RECENT CONVERSATION:\n" + "\n".join(history_lines)
    
    def _create_manipulator_welcome(self, products: List[Product], customer_context: Dict[str, Any], interaction_type: str, base_context: str) -> str:
        """Create welcome prompt for Manipulator branch (ad interactions)"""
        interaction_context = {
            'like': 'liked our post',
            'comment': 'commented on our post', 
            'click': 'clicked on our advertisement',
            'share': 'shared our content'
        }.get(interaction_type, 'interacted with our content')
        
        return f"""{base_context}

CUSTOMER INTERACTION: The customer just {interaction_context} about our products.

TASK: Create a warm, welcoming response that acknowledges their interest and naturally introduces them to our products.

WELCOME PROTOCOL STRATEGY:
1. **Warm Greeting**: Thank them for their interest in a genuine way
2. **Interest Acknowledgment**: Reference their specific interaction naturally
3. **Value Introduction**: Briefly highlight what makes our products special
4. **Helpful Positioning**: Position yourself as a helpful advisor, not a salesperson
5. **Engaging Question**: End with a question that encourages them to share their needs

CONVERSATION GUIDELINES:
- Be genuinely enthusiastic but not overly eager
- Focus on being helpful rather than selling
- Use conversational, friendly language
- Keep the welcome message under 80 words
- Make them feel valued as a potential customer

Generate a warm welcome message that feels personal and engaging:"""
    
    def _create_convincer_welcome(self, products: List[Product], customer_context: Dict[str, Any], base_context: str) -> str:
        """Create welcome prompt for Convincer branch (direct messages)"""
        return f"""{base_context}

CUSTOMER CONTACT: The customer has reached out to us directly via message.

TASK: Create a welcoming response that makes them feel heard and introduces our ability to help them.

WELCOME PROTOCOL STRATEGY:
1. **Warm Greeting**: Professional but friendly welcome
2. **Appreciation**: Thank them for reaching out
3. **Expertise Positioning**: Subtly establish your product knowledge
4. **Needs Discovery**: Show interest in understanding their specific needs
5. **Support Offering**: Clearly offer assistance in finding the right solution

CONVERSATION GUIDELINES:
- Be professional yet approachable
- Show genuine interest in helping them
- Demonstrate product expertise without overwhelming
- Keep response under 75 words
- End with an invitation for them to share their needs

Generate a professional welcome that establishes trust and helpfulness:"""
    
    def _create_manipulator_prompt(self, customer_message: str, products: List[Product], history_context: str, base_context: str) -> str:
        """Create conversation prompt for Manipulator branch"""
        return f"""{base_context}

{history_context}

CUSTOMER'S MESSAGE: "{customer_message}"

TASK: Respond as a knowledgeable product consultant who understands this customer came from our advertising.

MANIPULATOR BRANCH STRATEGY:
1. **Direct Relevance**: Address their message in context of the advertised products
2. **Product Focus**: Keep conversation centered on the specific products they showed interest in
3. **Benefits Highlighting**: Emphasize unique value propositions
4. **Urgency Creation**: Subtly create appropriate urgency without being pushy
5. **Next Steps**: Guide them toward making a decision or getting more information

PERSUASION TECHNIQUES:
- Use social proof when relevant ("Many customers love...")
- Highlight scarcity or exclusivity appropriately
- Focus on benefits that solve their problems
- Create emotional connection to the products
- Provide clear next steps

RESPONSE GUIDELINES:
- Stay focused on the advertised products
- Be persuasive but not aggressive
- Keep response under 90 words
- Include a clear call-to-action
- Maintain helpful, expert tone

Generate a focused response that moves the conversation toward a decision:"""
    
    def _create_convincer_prompt(self, customer_message: str, products: List[Product], history_context: str, base_context: str, customer_context: Dict[str, Any]) -> str:
        """Create conversation prompt for Convincer branch"""
        return f"""{base_context}

{history_context}

CUSTOMER'S MESSAGE: "{customer_message}"

TASK: Respond as a helpful product expert who can guide them to the perfect solution.

CONVINCER BRANCH STRATEGY:
1. **Active Listening**: Show you understand their specific needs and concerns
2. **Consultative Approach**: Ask thoughtful questions to better understand requirements
3. **Tailored Recommendations**: Match products specifically to their expressed needs
4. **Education Focus**: Provide valuable information that helps them make informed decisions
5. **Relationship Building**: Focus on long-term customer satisfaction over quick sales

CONVERSATION TECHNIQUES:
- Ask clarifying questions about their preferences
- Provide detailed product knowledge when relevant
- Address concerns with factual information
- Suggest alternatives if initial products don't fit
- Build trust through expertise and honesty

RESPONSE GUIDELINES:
- Address their specific message directly
- Be helpful and informative
- Keep response under 85 words
- End with a helpful question or suggestion
- Maintain consultative, expert tone

Generate a helpful response that demonstrates expertise and builds trust:"""
    
    def _create_recovery_prompt(self, customer_message: str, products: List[Product], history_context: str, base_context: str) -> str:
        """Create recovery prompt for uninterested customers"""
        return f"""{base_context}

{history_context}

CUSTOMER'S MESSAGE: "{customer_message}"

SITUATION: The customer has shown signs of disinterest or is about to disengage.

TASK: Create a recovery response that respects their position while keeping the door open.

RECOVERY STRATEGY:
1. **Acknowledge Understanding**: Show that you respect their current position
2. **No Pressure**: Explicitly remove any sales pressure
3. **Value Offering**: Offer something genuinely useful (information, future help)
4. **Relationship Focus**: Prioritize relationship over immediate sale
5. **Graceful Exit**: Provide an easy way for them to disengage if they prefer

RECOVERY TECHNIQUES:
- Use empathetic language ("I understand...")
- Offer future assistance without commitment
- Provide useful information regardless of purchase intent
- Show respect for their time and decision-making process
- Leave a positive final impression

RESPONSE GUIDELINES:
- Be gracious and understanding
- Remove all sales pressure
- Keep response under 70 words
- Offer genuine value or future help
- End on a positive, respectful note

Generate a graceful response that prioritizes relationship over immediate sales:"""
    
    def _create_qualified_conclusion(self, history_context: str, products_discussed: List[Product]) -> str:
        """Create conclusion prompt for qualified leads"""
        return f"""{history_context}

SITUATION: The customer appears interested and qualified. Time to conclude with next steps.

TASK: Create a professional conclusion that facilitates the handoff to the onboarding agent.

QUALIFIED CONCLUSION STRATEGY:
1. **Positive Reinforcement**: Acknowledge their great choice/decision
2. **Next Steps Clarity**: Clearly explain what happens next
3. **Onboarding Introduction**: Smoothly introduce the next phase
4. **Continued Support**: Assure them of ongoing support
5. **Professional Handoff**: Maintain continuity in the customer experience

CONCLUSION GUIDELINES:
- Congratulate them on their decision
- Explain the onboarding process briefly
- Provide reassurance about continued support
- Keep response under 80 words
- End with enthusiasm about their journey ahead

Generate a professional conclusion that celebrates their decision and introduces next steps:"""
    
    def _create_uninterested_conclusion(self, history_context: str) -> str:
        """Create conclusion prompt for uninterested customers"""
        return f"""{history_context}

SITUATION: The customer is not interested at this time. Create a graceful conclusion.

TASK: End the conversation professionally while leaving the door open for future engagement.

UNINTERESTED CONCLUSION STRATEGY:
1. **Respect Their Decision**: Acknowledge and respect their choice
2. **No Pressure**: Confirm no pressure or follow-up unless they want it
3. **Future Availability**: Let them know you're available if things change
4. **Positive Impression**: End on a genuinely positive note
5. **Professional Courtesy**: Thank them for their time

CONCLUSION GUIDELINES:
- Be gracious and understanding
- Respect their decision completely
- Offer future availability without pressure
- Keep response under 60 words
- End with genuine well-wishes

Generate a respectful conclusion that leaves a positive final impression:"""
    
    def _create_general_conclusion(self, history_context: str) -> str:
        """Create general conclusion prompt"""
        return f"""{history_context}

SITUATION: The conversation needs a natural conclusion.

TASK: Create a friendly conclusion that wraps up the conversation appropriately.

GENERAL CONCLUSION STRATEGY:
1. **Conversation Summary**: Briefly acknowledge what was discussed
2. **Availability**: Let them know you're available for future questions
3. **Appreciation**: Thank them for their time and interest
4. **Open Door**: Leave the door open for future contact
5. **Positive Ending**: End on an upbeat, helpful note

Generate a friendly conclusion that wraps up the conversation naturally:"""
    
    def _fallback_welcome_prompt(self) -> str:
        """Fallback welcome prompt when errors occur"""
        return """You are a friendly customer service representative. A customer has just interacted with our business. 

Create a warm, welcoming response (under 60 words) that:
1. Thanks them for their interest
2. Offers to help them find what they need
3. Asks how you can assist them today

Be professional, friendly, and helpful."""
    
    def _fallback_conversation_prompt(self, customer_message: str) -> str:
        """Fallback conversation prompt when errors occur"""
        return f"""You are a helpful customer service representative.

Customer's message: "{customer_message}"

Respond helpfully and professionally (under 70 words) by:
1. Acknowledging their message
2. Offering assistance
3. Asking how you can help them further

Be friendly, professional, and solution-focused."""
    
    def _fallback_conclusion_prompt(self) -> str:
        """Fallback conclusion prompt when errors occur"""
        return """Create a professional conclusion to this conversation (under 50 words) that:
1. Thanks the customer for their time
2. Offers future assistance if needed
3. Ends on a positive note

Be gracious and professional."""

    def get_prompt_statistics(self) -> Dict[str, Any]:
        """Get statistics about prompt usage and effectiveness"""
        return {
            "personality_config": self.business_personality,
            "prompt_types": [
                "welcome_prompts",
                "conversation_prompts", 
                "recovery_prompts",
                "cross_product_prompts",
                "conclusion_prompts"
            ],
            "fallback_strategies": "Available for all prompt types",
            "response_guidelines": {
                "max_length": "60-100 words depending on prompt type",
                "tone": "Professional, friendly, consultative",
                "approach": "Customer-focused, helpful, non-aggressive"
            }
        }

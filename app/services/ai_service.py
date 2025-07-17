from openai import AsyncAzureOpenAI
from app.core.config import settings
from typing import List, Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Service class for Azure OpenAI API interactions"""
    
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment_name = settings.azure_openai_deployment_name
    
    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate a completion using Azure OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Azure OpenAI completion failed: {e}")
            # Return fallback response
            return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
    
    async def extract_keywords(self, customer_message: str, business_context: str) -> List[str]:
        """
        keyRetriever subsystem: Extract relevant keywords from customer message
        """
        try:
            prompt = f"""
You are an AI assistant that extracts product-related keywords from customer messages.

BUSINESS CONTEXT:
{business_context}

CUSTOMER MESSAGE:
"{customer_message}"

TASK:
Extract keywords from the customer message that are related to the business products. Focus on:
- Product types (smartphone, laptop, headphones, etc.)
- Product features (camera, battery, wireless, etc.)
- Use cases (work, gaming, music, etc.)
- Specifications (5G, noise-canceling, etc.)

Return ONLY a JSON array of keywords, nothing else. Example: ["smartphone", "camera", "photography"]
"""

            messages = [
                {"role": "system", "content": "You are a keyword extraction specialist. Return only JSON arrays."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.generate_completion(messages, max_tokens=200, temperature=0.3)
            
            # Parse JSON response
            try:
                keywords = json.loads(response)
                if isinstance(keywords, list):
                    logger.info(f"keyRetriever extracted keywords: {keywords}")
                    return keywords
                else:
                    logger.warning(f"keyRetriever returned non-list: {response}")
                    return []
            except json.JSONDecodeError:
                logger.warning(f"keyRetriever returned invalid JSON: {response}")
                # Fallback: extract keywords manually
                return self._fallback_keyword_extraction(customer_message)
                
        except Exception as e:
            logger.error(f"keyRetriever failed: {e}")
            return self._fallback_keyword_extraction(customer_message)
    
    def _fallback_keyword_extraction(self, message: str) -> List[str]:
        """Fallback keyword extraction without AI"""
        common_product_keywords = [
            "smartphone", "phone", "mobile", "laptop", "computer", "headphones",
            "audio", "wireless", "bluetooth", "camera", "gaming", "work",
            "productivity", "music", "video", "battery", "screen", "display"
        ]
        
        message_lower = message.lower()
        extracted = []
        
        for keyword in common_product_keywords:
            if keyword in message_lower:
                extracted.append(keyword)
        
        logger.info(f"Fallback keyword extraction: {extracted}")
        return extracted
    
    async def generate_conversation_response(
        self, 
        conversation_context: Dict[str, Any],
        customer_message: Optional[str] = None,
        is_welcome: bool = False
    ) -> str:
        """
        Generate AI conversation response based on context
        """
        try:
            # Build conversation prompt based on branch and context
            if conversation_context["branch"] == "manipulator":
                return await self._generate_manipulator_response(conversation_context, is_welcome)
            else:
                return await self._generate_convincer_response(conversation_context, customer_message, is_welcome)
                
        except Exception as e:
            logger.error(f"Conversation response generation failed: {e}")
            return "Thank you for your interest! I'm here to help you find the perfect product. How can I assist you today?"
    
    async def _generate_manipulator_response(
        self, 
        context: Dict[str, Any], 
        is_welcome: bool
    ) -> str:
        """Generate response for Manipulator branch (user clicked/liked ad)"""
        
        product_info = context.get("products", [])
        interaction_type = context.get("interaction_type", "interaction")
        
        if not product_info:
            return "Hello! Thank you for your interest in our products. How can I help you today?"
        
        product = product_info[0]  # Primary product from interaction
        
        if is_welcome:
            prompt = f"""
You are a friendly, professional sales representative for a technology company.

SITUATION: A customer just {interaction_type}d on an advertisement for this product:
- Product: {product.get('product_description', 'our product')}
- Price: {product.get('product_attributes', {}).get('price', 'Contact for pricing')}
- Key features: {', '.join(product.get('product_tag', []))}

TASK: Create a warm, human-like greeting message that:
1. Acknowledges their interest in the specific product
2. Highlights 1-2 key benefits of the product
3. Offers to help them learn more
4. Feels natural and conversational (not salesy)
5. Keep it under 100 words

Be enthusiastic but professional. Make it feel like a genuine human interaction.
"""
        else:
            # Follow-up conversation
            prompt = f"""
You are continuing a conversation about this product:
- Product: {product.get('product_description', 'our product')}
- Price: {product.get('product_attributes', {}).get('price', 'Contact for pricing')}

Continue the conversation naturally, providing helpful information and gently encouraging the customer to consider the product.
"""
        
        messages = [
            {"role": "system", "content": "You are a helpful, friendly sales representative."},
            {"role": "user", "content": prompt}
        ]
        
        return await self.generate_completion(messages, max_tokens=150, temperature=0.8)
    
    async def _generate_convincer_response(
        self, 
        context: Dict[str, Any], 
        customer_message: str, 
        is_welcome: bool
    ) -> str:
        """Generate response for Convincer branch (customer initiated contact)"""
        
        products = context.get("products", [])
        conversation_history = context.get("conversation_history", [])
        
        if is_welcome and products:
            # First response with product recommendations
            product_summaries = []
            for product in products[:3]:  # Top 3 matches
                summary = f"- {product.get('product_description', 'Product')[:60]}..."
                product_summaries.append(summary)
            
            prompt = f"""
You are a helpful sales representative responding to a customer inquiry.

CUSTOMER MESSAGE: "{customer_message}"

RECOMMENDED PRODUCTS based on their message:
{chr(10).join(product_summaries)}

TASK: Create a warm response that:
1. Acknowledges their message warmly
2. Shows you understand their needs
3. Introduces the relevant products naturally
4. Asks a follow-up question to engage them further
5. Keep it conversational and helpful (under 120 words)

Make it feel like a genuine, helpful human interaction.
"""
        else:
            # Build conversation history for context
            history_text = ""
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                sender = "Customer" if msg.get("sender") == "customer" else "You"
                history_text += f"{sender}: {msg.get('content', '')}\n"
            
            prompt = f"""
You are continuing a sales conversation.

CONVERSATION HISTORY:
{history_text}

CUSTOMER'S LATEST MESSAGE: "{customer_message}"

AVAILABLE PRODUCTS:
{chr(10).join([f"- {p.get('product_description', 'Product')[:50]}..." for p in products[:2]])}

Respond naturally and helpfully, addressing their message and gently guiding toward a purchase decision.
"""
        
        messages = [
            {"role": "system", "content": "You are a helpful, persuasive but not pushy sales representative."},
            {"role": "user", "content": prompt}
        ]
        
        return await self.generate_completion(messages, max_tokens=180, temperature=0.7)

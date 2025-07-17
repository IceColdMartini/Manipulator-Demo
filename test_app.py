"""
Minimal ManipulatorAI FastAPI Application for Testing
This version bypasses database connections for Swagger UI testing
"""

from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ManipulatorAI - Testing Mode",
    description="AI-powered conversation manipulation and webhook processing platform (Testing Mode)",
    version="1.0.0"
)

# Mock data for testing
MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "BasicCRM",
        "description": "Simple CRM solution for small businesses",
        "category": "crm",
        "target_audience": "small_business",
        "pricing": 29,
        "features": ["contact management", "deal tracking", "basic reporting"]
    },
    {
        "id": 2,
        "name": "ProCRM",
        "description": "Advanced CRM platform for enterprises",
        "category": "crm", 
        "target_audience": "enterprise",
        "pricing": 199,
        "features": ["advanced analytics", "automation", "integrations", "custom fields"]
    },
    {
        "id": 3,
        "name": "ProjectManager Pro",
        "description": "Comprehensive project management solution",
        "category": "project_management",
        "target_audience": "medium_business",
        "pricing": 99,
        "features": ["task management", "team collaboration", "time tracking", "reporting"]
    }
]

MOCK_CONVERSATIONS = {}

# Root endpoint
@app.get("/")
async def read_root():
    return {
        "message": "Welcome to ManipulatorAI (Testing Mode)",
        "version": "1.0.0",
        "status": "running",
        "mode": "testing",
        "endpoints": {
            "health": "/health",
            "webhooks": "/webhook/facebook, /webhook/instagram",
            "conversations": "/conversation/message",
            "products": "/products/, /products/search",
            "ai_testing": "/ai/extract-keywords, /ai/match-products"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "testing",
        "databases": {
            "postgresql": "mocked",
            "mongodb": "mocked", 
            "redis": "mocked"
        }
    }

# Webhook endpoints
@app.get("/webhook/facebook")
async def facebook_webhook_verification(
    hub_mode: Optional[str] = None,
    hub_verify_token: Optional[str] = None,
    hub_challenge: Optional[str] = None
):
    """Facebook webhook verification endpoint"""
    if hub_mode == "subscribe" and hub_verify_token == "test_facebook_verify_token":
        return hub_challenge
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/webhook/facebook")
async def facebook_webhook_handler(payload: Dict[str, Any]):
    """Handle Facebook webhook events"""
    logger.info(f"Received Facebook webhook: {payload}")
    return {
        "status": "success",
        "message": "Webhook processed successfully (mocked)",
        "task_id": f"webhook_task_{datetime.now().timestamp()}"
    }

@app.get("/webhook/instagram")
async def instagram_webhook_verification(
    hub_mode: Optional[str] = None,
    hub_verify_token: Optional[str] = None,
    hub_challenge: Optional[str] = None
):
    """Instagram webhook verification endpoint"""
    if hub_mode == "subscribe" and hub_verify_token == "test_instagram_verify_token":
        return hub_challenge
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/webhook/instagram")
async def instagram_webhook_handler(payload: Dict[str, Any]):
    """Handle Instagram webhook events"""
    logger.info(f"Received Instagram webhook: {payload}")
    return {
        "status": "success",
        "message": "Webhook processed successfully (mocked)",
        "task_id": f"webhook_task_{datetime.now().timestamp()}"
    }

# Conversation endpoints
@app.post("/conversation/message")
async def process_customer_message(payload: Dict[str, Any]):
    """Process incoming customer message"""
    customer_id = payload.get("customer_id", "unknown")
    message = payload.get("message", "")
    conversation_branch = payload.get("conversation_branch", "manipulator")
    customer_context = payload.get("customer_context", {})
    
    # Generate mock conversation ID
    conversation_id = f"conv_{datetime.now().timestamp()}"
    
    # Mock AI response based on branch
    if conversation_branch == "manipulator":
        response = f"Hi! Great to hear from you! I'm excited you're interested in our products. Based on your message about '{message}', I think our solutions could be perfect for you. Would you like me to show you how we can help your business grow?"
        next_actions = ["product_demo", "feature_highlight", "pricing_discussion"]
    else:  # convincer branch
        response = f"Hello! I'd love to help you find the perfect solution. You mentioned '{message}' - could you tell me more about your specific challenges and what you're hoping to achieve?"
        next_actions = ["needs_discovery", "pain_point_analysis", "solution_matching"]
    
    # Store in mock conversations
    MOCK_CONVERSATIONS[conversation_id] = {
        "customer_id": customer_id,
        "messages": [
            {
                "timestamp": datetime.now().isoformat(),
                "sender": "customer",
                "content": message
            },
            {
                "timestamp": datetime.now().isoformat(),
                "sender": "ai",
                "content": response
            }
        ],
        "branch": conversation_branch,
        "context": customer_context,
        "state": "active"
    }
    
    return {
        "conversation_id": conversation_id,
        "response": response,
        "conversation_branch": conversation_branch,
        "conversation_state": "active",
        "next_actions": next_actions,
        "context": customer_context
    }

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation by ID"""
    if conversation_id in MOCK_CONVERSATIONS:
        return {
            "conversation_id": conversation_id,
            "conversation": MOCK_CONVERSATIONS[conversation_id]
        }
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.post("/conversation/{conversation_id}/message")
async def continue_conversation(conversation_id: str, payload: Dict[str, Any]):
    """Continue an existing conversation"""
    if conversation_id not in MOCK_CONVERSATIONS:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    message = payload.get("message", "")
    conversation = MOCK_CONVERSATIONS[conversation_id]
    
    # Mock AI response for continuation
    response = f"I understand your point about '{message}'. Let me provide you with more detailed information that addresses your specific needs. Based on our conversation so far, I recommend we explore some specific solutions that would work perfectly for your situation."
    
    # Add messages to conversation
    conversation["messages"].extend([
        {
            "timestamp": datetime.now().isoformat(),
            "sender": "customer",
            "content": message
        },
        {
            "timestamp": datetime.now().isoformat(),
            "sender": "ai",
            "content": response
        }
    ])
    
    return {
        "conversation_id": conversation_id,
        "response": response,
        "conversation_state": "continued",
        "next_actions": ["deeper_exploration", "solution_presentation"]
    }

# Product endpoints
@app.get("/products/")
async def get_products():
    """Get all products"""
    return {
        "products": MOCK_PRODUCTS,
        "total": len(MOCK_PRODUCTS)
    }

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get product by ID"""
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if product:
        return product
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@app.post("/products/search")
async def search_products(payload: Dict[str, Any]):
    """Search products"""
    query = payload.get("query", "").lower()
    category = payload.get("category", "")
    target_audience = payload.get("target_audience", "")
    
    filtered_products = MOCK_PRODUCTS
    
    if query:
        filtered_products = [p for p in filtered_products if query in p["name"].lower() or query in p["description"].lower()]
    
    if category:
        filtered_products = [p for p in filtered_products if p["category"] == category]
        
    if target_audience:
        filtered_products = [p for p in filtered_products if p["target_audience"] == target_audience]
    
    return {
        "products": filtered_products,
        "total": len(filtered_products),
        "query": query
    }

# AI Testing endpoints
@app.post("/ai/extract-keywords")
async def extract_keywords(payload: Dict[str, Any]):
    """Extract keywords from customer message"""
    message = payload.get("message", "")
    
    # Mock keyword extraction
    mock_keywords = []
    if "crm" in message.lower():
        mock_keywords.extend(["crm", "customer_management", "sales"])
    if "project" in message.lower():
        mock_keywords.extend(["project_management", "team_collaboration"])
    if "small business" in message.lower():
        mock_keywords.extend(["small_business", "startup", "growing_company"])
    if "enterprise" in message.lower():
        mock_keywords.extend(["enterprise", "large_scale", "corporate"])
    
    if not mock_keywords:
        mock_keywords = ["general_inquiry", "business_software", "solution_seeking"]
    
    return {
        "keywords": mock_keywords,
        "confidence": 0.85,
        "message_intent": "product_inquiry",
        "urgency_level": "medium"
    }

@app.post("/ai/match-products")
async def match_products(payload: Dict[str, Any]):
    """Match products to customer message"""
    customer_message = payload.get("customer_message", "")
    customer_context = payload.get("customer_context", {})
    
    # Mock product matching logic
    matched_products = []
    
    if "crm" in customer_message.lower():
        if customer_context.get("company_size") == "small_business":
            matched_products.append({
                "id": 1,
                "name": "BasicCRM",
                "match_score": 0.92,
                "match_reasons": ["perfect for small business", "budget-friendly", "easy to use"]
            })
        else:
            matched_products.append({
                "id": 2,
                "name": "ProCRM",
                "match_score": 0.88,
                "match_reasons": ["enterprise features", "scalable", "advanced analytics"]
            })
    
    if "project" in customer_message.lower():
        matched_products.append({
            "id": 3,
            "name": "ProjectManager Pro",
            "match_score": 0.89,
            "match_reasons": ["comprehensive project tools", "team collaboration", "time tracking"]
        })
    
    if not matched_products:
        # Default recommendation
        matched_products.append({
            "id": 1,
            "name": "BasicCRM",
            "match_score": 0.65,
            "match_reasons": ["versatile solution", "good starting point"]
        })
    
    return {
        "matched_products": matched_products,
        "total_matches": len(matched_products),
        "conversation_suggestions": [
            f"Would you like me to show you how {matched_products[0]['name']} can help your business?",
            "I can walk you through the key features that make this perfect for your needs.",
            "Would you like to see a quick demo or learn more about pricing?"
        ]
    }

@app.post("/ai/full-pipeline")
async def full_ai_pipeline(payload: Dict[str, Any]):
    """Complete AI processing pipeline"""
    customer_message = payload.get("customer_message", "")
    customer_context = payload.get("customer_context", {})
    
    # Combine keyword extraction and product matching
    keywords_result = await extract_keywords({"message": customer_message})
    products_result = await match_products({
        "customer_message": customer_message,
        "customer_context": customer_context
    })
    
    return {
        "keywords": keywords_result,
        "product_matches": products_result,
        "recommended_response": f"Based on your message about '{customer_message}', I can see you're interested in {keywords_result['keywords'][0] if keywords_result['keywords'] else 'business solutions'}. Our {products_result['matched_products'][0]['name'] if products_result['matched_products'] else 'recommended solution'} would be perfect for your needs!",
        "next_steps": ["schedule_demo", "provide_pricing", "answer_questions"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

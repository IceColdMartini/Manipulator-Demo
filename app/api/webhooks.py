from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from typing import Dict, Any
from app.models.schemas import FacebookWebhookPayload, InstagramWebhookPayload
from app.core.config import settings
from app.core.database import get_redis_client
import logging
import hashlib
import hmac

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhooks"])

def verify_facebook_signature(payload: bytes, signature: str) -> bool:
    """Verify Facebook webhook signature for security"""
    try:
        # Facebook sends signature as 'sha256=<hash>'
        expected_signature = hmac.new(
            settings.facebook_verify_token.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Facebook signature verification failed: {e}")
        return False

def verify_instagram_signature(payload: bytes, signature: str) -> bool:
    """Verify Instagram webhook signature for security"""
    try:
        # Instagram uses similar signature format to Facebook
        expected_signature = hmac.new(
            settings.instagram_verify_token.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Instagram signature verification failed: {e}")
        return False

@router.get("/facebook")
async def facebook_webhook_verification(request: Request):
    """Facebook webhook verification endpoint"""
    try:
        # Get query parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        logger.info(f"Facebook webhook verification: mode={mode}, token_match={token == settings.facebook_verify_token}")
        
        # Verify the webhook
        if mode == "subscribe" and token == settings.facebook_verify_token:
            logger.info("Facebook webhook verified successfully")
            return PlainTextResponse(challenge)
        else:
            logger.warning("Facebook webhook verification failed")
            raise HTTPException(status_code=403, detail="Forbidden")
            
    except Exception as e:
        logger.error(f"Facebook webhook verification error: {e}")
        raise HTTPException(status_code=400, detail="Bad Request")

@router.post("/facebook")
async def facebook_webhook_handler(
    request: Request,
    redis_client = Depends(get_redis_client)
):
    """Handle Facebook webhook events"""
    try:
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        
        # Verify signature (in production, uncomment this)
        # if not verify_facebook_signature(body, signature):
        #     logger.warning("Facebook webhook signature verification failed")
        #     raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse JSON payload
        import json
        payload_data = json.loads(body.decode('utf-8'))
        
        logger.info(f"Received Facebook webhook: {payload_data}")
        
        # Queue the webhook for processing
        queue_key = "facebook_webhook_queue"
        await redis_client.lpush(queue_key, json.dumps({
            "source": "facebook",
            "timestamp": "2025-07-13T16:30:00Z",
            "payload": payload_data
        }))
        
        logger.info("Facebook webhook queued for processing")
        return {"status": "success", "message": "Webhook received and queued"}
        
    except json.JSONDecodeError as e:
        logger.error(f"Facebook webhook JSON parsing error: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Facebook webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/instagram")
async def instagram_webhook_verification(request: Request):
    """Instagram webhook verification endpoint"""
    try:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        logger.info(f"Instagram webhook verification: mode={mode}, token_match={token == settings.instagram_verify_token}")
        
        if mode == "subscribe" and token == settings.instagram_verify_token:
            logger.info("Instagram webhook verified successfully")
            return PlainTextResponse(challenge)
        else:
            logger.warning("Instagram webhook verification failed")
            raise HTTPException(status_code=403, detail="Forbidden")
            
    except Exception as e:
        logger.error(f"Instagram webhook verification error: {e}")
        raise HTTPException(status_code=400, detail="Bad Request")

@router.post("/instagram")
async def instagram_webhook_handler(
    request: Request,
    redis_client = Depends(get_redis_client)
):
    """Handle Instagram webhook events"""
    try:
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        
        # Verify signature (in production, uncomment this)
        # if not verify_instagram_signature(body, signature):
        #     logger.warning("Instagram webhook signature verification failed")
        #     raise HTTPException(status_code=403, detail="Invalid signature")
        
        import json
        payload_data = json.loads(body.decode('utf-8'))
        
        logger.info(f"Received Instagram webhook: {payload_data}")
        
        # Queue the webhook for processing
        queue_key = "instagram_webhook_queue"
        await redis_client.lpush(queue_key, json.dumps({
            "source": "instagram",
            "timestamp": "2025-07-13T16:30:00Z",
            "payload": payload_data
        }))
        
        logger.info("Instagram webhook queued for processing")
        return {"status": "success", "message": "Webhook received and queued"}
        
    except json.JSONDecodeError as e:
        logger.error(f"Instagram webhook JSON parsing error: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Instagram webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

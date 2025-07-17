"""
Webhook Tasks for Asynchronous Processing
Handles incoming webhook events in the background
"""

from celery import current_task
from app.core.celery_app import celery_app
from app.core.config import settings
from app.tasks.conversation_tasks import process_manipulator_interaction_task
from typing import Dict, Any, Optional
import asyncio
import logging
import json
import httpx
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

@celery_app.task(bind=True, name="process_facebook_webhook")
def process_facebook_webhook_task(self, webhook_data: Dict[str, Any]):
    """
    Asynchronously process Facebook webhook events
    """
    try:
        task_id = self.request.id
        logger.info(f"Processing Facebook webhook task {task_id}")
        
        self.update_state(
            state="PROCESSING",
            meta={
                "webhook_type": "facebook",
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        # Extract relevant data from Facebook webhook
        entries = webhook_data.get("entry", [])
        processed_interactions = []
        
        for i, entry in enumerate(entries):
            try:
                # Update progress
                progress = int((i / len(entries)) * 90)
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "webhook_type": "facebook",
                        "progress": progress,
                        "status": f"Processing entry {i + 1}/{len(entries)}"
                    }
                )
                
                # Process different Facebook event types
                if "changes" in entry:
                    # Page events (likes, comments, etc.)
                    for change in entry["changes"]:
                        interaction = process_facebook_page_event(change, entry.get("id"))
                        if interaction:
                            # Trigger manipulator conversation asynchronously
                            process_manipulator_interaction_task.delay(
                                customer_id=interaction["customer_id"],
                                business_id=interaction["business_id"],
                                interaction_data=interaction["interaction_data"]
                            )
                            processed_interactions.append(interaction)
                
                elif "messaging" in entry:
                    # Direct messages
                    for message_event in entry["messaging"]:
                        interaction = process_facebook_message_event(message_event)
                        if interaction:
                            processed_interactions.append(interaction)
                            
            except Exception as e:
                logger.error(f"Error processing Facebook entry {i}: {e}")
                continue
        
        # Final success state
        self.update_state(
            state="SUCCESS",
            meta={
                "webhook_type": "facebook",
                "progress": 100,
                "status": "Completed successfully",
                "completed_at": datetime.utcnow().isoformat(),
                "processed_interactions": len(processed_interactions),
                "interactions": processed_interactions
            }
        )
        
        logger.info(f"Successfully processed Facebook webhook task {task_id}")
        return {
            "processed_interactions": len(processed_interactions),
            "interactions": processed_interactions
        }
        
    except Exception as e:
        logger.error(f"Error in Facebook webhook task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "webhook_type": "facebook",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

@celery_app.task(bind=True, name="process_google_webhook")
def process_google_webhook_task(self, webhook_data: Dict[str, Any]):
    """
    Asynchronously process Google Ads webhook events
    """
    try:
        task_id = self.request.id
        logger.info(f"Processing Google webhook task {task_id}")
        
        self.update_state(
            state="PROCESSING",
            meta={
                "webhook_type": "google",
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        # Extract Google Ads interaction data
        processed_interactions = []
        
        # Process Google Ads click events
        if webhook_data.get("event_type") == "click":
            interaction = process_google_click_event(webhook_data)
            if interaction:
                # Trigger manipulator conversation asynchronously
                process_manipulator_interaction_task.delay(
                    customer_id=interaction["customer_id"],
                    business_id=interaction["business_id"],
                    interaction_data=interaction["interaction_data"]
                )
                processed_interactions.append(interaction)
        
        # Process Google Ads conversion events
        elif webhook_data.get("event_type") == "conversion":
            interaction = process_google_conversion_event(webhook_data)
            if interaction:
                processed_interactions.append(interaction)
        
        self.update_state(
            state="SUCCESS",
            meta={
                "webhook_type": "google",
                "progress": 100,
                "status": "Completed successfully",
                "completed_at": datetime.utcnow().isoformat(),
                "processed_interactions": len(processed_interactions),
                "interactions": processed_interactions
            }
        )
        
        logger.info(f"Successfully processed Google webhook task {task_id}")
        return {
            "processed_interactions": len(processed_interactions),
            "interactions": processed_interactions
        }
        
    except Exception as e:
        logger.error(f"Error in Google webhook task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "webhook_type": "google",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

@celery_app.task(bind=True, name="process_generic_webhook")
def process_generic_webhook_task(self, webhook_data: Dict[str, Any], platform: str = "unknown"):
    """
    Asynchronously process generic webhook events from any platform
    """
    try:
        task_id = self.request.id
        logger.info(f"Processing generic webhook task {task_id} for platform {platform}")
        
        self.update_state(
            state="PROCESSING",
            meta={
                "webhook_type": "generic",
                "platform": platform,
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        # Extract standard fields from webhook data
        interaction_data = {
            "customer_id": webhook_data.get("customer_id", f"webhook_{datetime.utcnow().timestamp()}"),
            "business_id": webhook_data.get("business_id", "default_business"),
            "product_id": webhook_data.get("product_id"),
            "type": webhook_data.get("interaction_type", "webhook"),
            "platform": platform,
            "timestamp": datetime.utcnow().isoformat(),
            "raw_data": webhook_data
        }
        
        self.update_state(
            state="PROCESSING",
            meta={
                "webhook_type": "generic",
                "platform": platform,
                "progress": 50,
                "status": "Processing interaction data"
            }
        )
        
        # If this looks like a manipulator interaction, process it
        if interaction_data.get("product_id"):
            process_manipulator_interaction_task.delay(
                customer_id=interaction_data["customer_id"],
                business_id=interaction_data["business_id"],
                interaction_data=interaction_data
            )
        
        self.update_state(
            state="SUCCESS",
            meta={
                "webhook_type": "generic",
                "platform": platform,
                "progress": 100,
                "status": "Completed successfully",
                "completed_at": datetime.utcnow().isoformat(),
                "interaction_data": interaction_data
            }
        )
        
        logger.info(f"Successfully processed generic webhook task {task_id}")
        return {"interaction_data": interaction_data}
        
    except Exception as e:
        logger.error(f"Error in generic webhook task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "webhook_type": "generic",
                "platform": platform,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

@celery_app.task(bind=True, name="send_webhook_response")
def send_webhook_response_task(self, webhook_url: str, response_data: Dict[str, Any]):
    """
    Asynchronously send response back to webhook source
    """
    try:
        task_id = self.request.id
        logger.info(f"Sending webhook response task {task_id} to {webhook_url}")
        
        self.update_state(
            state="PROCESSING",
            meta={
                "webhook_url": webhook_url,
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        async def send_response():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=response_data,
                    timeout=30.0
                )
                return {
                    "status_code": response.status_code,
                    "response_text": response.text,
                    "success": response.status_code < 400
                }
        
        # Send the webhook response
        result = run_async_task(send_response())
        
        self.update_state(
            state="SUCCESS",
            meta={
                "webhook_url": webhook_url,
                "progress": 100,
                "status": "Response sent successfully",
                "completed_at": datetime.utcnow().isoformat(),
                "result": result
            }
        )
        
        logger.info(f"Successfully sent webhook response task {task_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in webhook response task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "webhook_url": webhook_url,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

def process_facebook_page_event(change_data: Dict[str, Any], page_id: str) -> Optional[Dict[str, Any]]:
    """Process Facebook page events (likes, comments, shares)"""
    try:
        field = change_data.get("field")
        value = change_data.get("value", {})
        
        if field == "feed":
            # Post interactions
            item = value.get("item", "")
            verb = value.get("verb", "")
            sender_id = value.get("sender_id")
            
            if verb in ["like", "comment", "share"] and sender_id:
                return {
                    "customer_id": f"fb_{sender_id}",
                    "business_id": f"fb_page_{page_id}",
                    "interaction_data": {
                        "type": verb,
                        "platform": "facebook",
                        "post_id": item,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Error processing Facebook page event: {e}")
        return None

def process_facebook_message_event(message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process Facebook direct message events"""
    try:
        sender = message_data.get("sender", {})
        recipient = message_data.get("recipient", {})
        message = message_data.get("message", {})
        
        if sender.get("id") and message.get("text"):
            return {
                "customer_id": f"fb_{sender['id']}",
                "business_id": f"fb_page_{recipient.get('id', 'unknown')}",
                "interaction_data": {
                    "type": "message",
                    "platform": "facebook",
                    "message": message["text"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error processing Facebook message event: {e}")
        return None

def process_google_click_event(webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process Google Ads click events"""
    try:
        click_id = webhook_data.get("click_id")
        customer_id = webhook_data.get("customer_id", f"google_{click_id}")
        campaign_id = webhook_data.get("campaign_id")
        ad_group_id = webhook_data.get("ad_group_id")
        
        return {
            "customer_id": customer_id,
            "business_id": webhook_data.get("business_id", "google_ads_account"),
            "interaction_data": {
                "type": "ad_click",
                "platform": "google_ads",
                "click_id": click_id,
                "campaign_id": campaign_id,
                "ad_group_id": ad_group_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing Google click event: {e}")
        return None

def process_google_conversion_event(webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process Google Ads conversion events"""
    try:
        conversion_id = webhook_data.get("conversion_id")
        customer_id = webhook_data.get("customer_id", f"google_conv_{conversion_id}")
        
        return {
            "customer_id": customer_id,
            "business_id": webhook_data.get("business_id", "google_ads_account"),
            "interaction_data": {
                "type": "conversion",
                "platform": "google_ads",
                "conversion_id": conversion_id,
                "conversion_value": webhook_data.get("conversion_value"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing Google conversion event: {e}")
        return None

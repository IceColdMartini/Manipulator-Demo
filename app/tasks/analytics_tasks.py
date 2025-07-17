"""
Analytics Tasks for Asynchronous Processing
Handles analytics, reporting, and performance monitoring tasks
"""

from celery import current_task
from app.core.celery_app import celery_app
from app.core.config import settings
from typing import Dict, Any, Optional, List
import asyncio
import logging
import json
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger(__name__)

def run_async_task(coro):
    """Helper to run async functions in Celery tasks"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

@celery_app.task(bind=True, name="generate_conversation_analytics")
def generate_conversation_analytics_task(
    self,
    start_date: str,
    end_date: str,
    business_id: Optional[str] = None
):
    """
    Generate comprehensive conversation analytics for a date range
    """
    try:
        task_id = self.request.id
        logger.info(f"Generating conversation analytics task {task_id}")
        
        self.update_state(
            state="PROCESSING",
            meta={
                "start_date": start_date,
                "end_date": end_date,
                "business_id": business_id,
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        async def generate_analytics():
            from app.core.database import async_session_maker, get_mongo_client
            from app.services.conversation_service import ConversationService
            
            # Initialize database connections
            async with async_session_maker() as postgres_session:
                mongo_client = get_mongo_client()
                mongo_db = mongo_client[settings.MONGO_DB_NAME]
                conversation_service = ConversationService(mongo_db)
                
                # Update progress
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": 10,
                        "status": "Database connections established"
                    }
                )
                
                # Parse dates
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
                
                # Fetch conversations in date range
                conversations = await conversation_service.get_conversations_by_date_range(
                    start_date=start_dt,
                    end_date=end_dt,
                    business_id=business_id
                )
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": 30,
                        "status": f"Retrieved {len(conversations)} conversations"
                    }
                )
                
                # Calculate analytics
                analytics = {
                    "period": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "business_id": business_id
                    },
                    "conversation_metrics": calculate_conversation_metrics(conversations),
                    "branch_performance": analyze_branch_performance(conversations),
                    "customer_engagement": analyze_customer_engagement(conversations),
                    "conversion_funnel": analyze_conversion_funnel(conversations),
                    "time_analysis": analyze_conversation_timing(conversations)
                }
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": 80,
                        "status": "Analytics calculations completed"
                    }
                )
                
                return analytics
        
        # Run the async analytics generation
        analytics = run_async_task(generate_analytics())
        
        # Final success state
        self.update_state(
            state="SUCCESS",
            meta={
                "progress": 100,
                "status": "Analytics generation completed",
                "completed_at": datetime.utcnow().isoformat(),
                "analytics": analytics
            }
        )
        
        logger.info(f"Successfully generated conversation analytics task {task_id}")
        return analytics
        
    except Exception as e:
        logger.error(f"Error in conversation analytics task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

@celery_app.task(bind=True, name="generate_performance_report")
def generate_performance_report_task(self, report_type: str = "daily"):
    """
    Generate system performance reports
    """
    try:
        task_id = self.request.id
        logger.info(f"Generating performance report task {task_id} - type: {report_type}")
        
        self.update_state(
            state="PROCESSING",
            meta={
                "report_type": report_type,
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        async def generate_report():
            from app.core.database import async_session_maker, get_mongo_client
            from app.services.enhanced_conversation_engine import EnhancedConversationEngine
            from app.services.ai_service import AzureOpenAIService
            from app.services.product_service import ProductService
            from app.services.conversation_service import ConversationService
            
            # Initialize services
            async with async_session_maker() as postgres_session:
                mongo_client = get_mongo_client()
                mongo_db = mongo_client[settings.MONGO_DB_NAME]
                
                ai_service = AzureOpenAIService()
                product_service = ProductService(postgres_session)
                conversation_service = ConversationService(mongo_db)
                
                engine = EnhancedConversationEngine(
                    ai_service=ai_service,
                    product_service=product_service,
                    conversation_service=conversation_service
                )
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": 25,
                        "status": "Services initialized"
                    }
                )
                
                # Get engine performance metrics
                engine_performance = await engine.get_engine_performance()
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": 50,
                        "status": "Engine performance retrieved"
                    }
                )
                
                # Calculate date range based on report type
                end_date = datetime.utcnow()
                if report_type == "daily":
                    start_date = end_date - timedelta(days=1)
                elif report_type == "weekly":
                    start_date = end_date - timedelta(days=7)
                elif report_type == "monthly":
                    start_date = end_date - timedelta(days=30)
                else:
                    start_date = end_date - timedelta(days=1)
                
                # Get system health metrics
                system_health = await get_system_health_metrics()
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": 75,
                        "status": "System health metrics collected"
                    }
                )
                
                # Compile performance report
                report = {
                    "report_type": report_type,
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    },
                    "engine_performance": engine_performance,
                    "system_health": system_health,
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                return report
        
        # Run the async report generation
        report = run_async_task(generate_report())
        
        # Final success state
        self.update_state(
            state="SUCCESS",
            meta={
                "progress": 100,
                "status": "Performance report generated",
                "completed_at": datetime.utcnow().isoformat(),
                "report": report
            }
        )
        
        logger.info(f"Successfully generated performance report task {task_id}")
        return report
        
    except Exception as e:
        logger.error(f"Error in performance report task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

@celery_app.task(bind=True, name="cleanup_old_data")
def cleanup_old_data_task(self, days_to_keep: int = 90):
    """
    Clean up old conversation data and task results
    """
    try:
        task_id = self.request.id
        logger.info(f"Cleaning up old data task {task_id} - keeping {days_to_keep} days")
        
        self.update_state(
            state="PROCESSING",
            meta={
                "days_to_keep": days_to_keep,
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
        )
        
        async def cleanup_data():
            from app.core.database import async_session_maker, get_mongo_client
            from app.services.conversation_service import ConversationService
            
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            async with async_session_maker() as postgres_session:
                mongo_client = get_mongo_client()
                mongo_db = mongo_client[settings.MONGO_DB_NAME]
                conversation_service = ConversationService(mongo_db)
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": 25,
                        "status": "Database connections established"
                    }
                )
                
                # Clean up old conversations
                deleted_conversations = await conversation_service.delete_conversations_before_date(cutoff_date)
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": 50,
                        "status": f"Deleted {deleted_conversations} old conversations"
                    }
                )
                
                # Clean up Celery result backend (Redis)
                from app.core.database import get_redis_client
                redis_client = get_redis_client()
                
                # Clean up old task results
                cleaned_keys = 0
                pattern = f"celery-task-meta-*"
                async for key in redis_client.scan_iter(match=pattern):
                    # Check if result is old enough to delete
                    ttl = await redis_client.ttl(key)
                    if ttl <= 0 or ttl > (days_to_keep * 24 * 3600):
                        await redis_client.delete(key)
                        cleaned_keys += 1
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": 90,
                        "status": f"Cleaned {cleaned_keys} old task results"
                    }
                )
                
                return {
                    "deleted_conversations": deleted_conversations,
                    "cleaned_task_results": cleaned_keys,
                    "cutoff_date": cutoff_date.isoformat()
                }
        
        # Run the async cleanup
        cleanup_result = run_async_task(cleanup_data())
        
        # Final success state
        self.update_state(
            state="SUCCESS",
            meta={
                "progress": 100,
                "status": "Data cleanup completed",
                "completed_at": datetime.utcnow().isoformat(),
                "cleanup_result": cleanup_result
            }
        )
        
        logger.info(f"Successfully completed data cleanup task {task_id}")
        return cleanup_result
        
    except Exception as e:
        logger.error(f"Error in data cleanup task: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        raise

# Analytics helper functions

def calculate_conversation_metrics(conversations: List[Dict]) -> Dict[str, Any]:
    """Calculate basic conversation metrics"""
    if not conversations:
        return {"total_conversations": 0}
    
    total = len(conversations)
    active = sum(1 for c in conversations if c.get("status") == "active")
    qualified = sum(1 for c in conversations if c.get("status") == "qualified")
    uninterested = sum(1 for c in conversations if c.get("status") == "uninterested")
    
    return {
        "total_conversations": total,
        "active_conversations": active,
        "qualified_conversations": qualified,
        "uninterested_conversations": uninterested,
        "qualification_rate": qualified / total if total > 0 else 0,
        "engagement_rate": (active + qualified) / total if total > 0 else 0
    }

def analyze_branch_performance(conversations: List[Dict]) -> Dict[str, Any]:
    """Analyze performance by conversation branch"""
    manipulator_convs = [c for c in conversations if c.get("conversation_branch") == "MANIPULATOR"]
    convincer_convs = [c for c in conversations if c.get("conversation_branch") == "CONVINCER"]
    
    return {
        "manipulator": {
            "total": len(manipulator_convs),
            "qualified": sum(1 for c in manipulator_convs if c.get("status") == "qualified"),
            "qualification_rate": sum(1 for c in manipulator_convs if c.get("status") == "qualified") / len(manipulator_convs) if manipulator_convs else 0
        },
        "convincer": {
            "total": len(convincer_convs),
            "qualified": sum(1 for c in convincer_convs if c.get("status") == "qualified"),
            "qualification_rate": sum(1 for c in convincer_convs if c.get("status") == "qualified") / len(convincer_convs) if convincer_convs else 0
        }
    }

def analyze_customer_engagement(conversations: List[Dict]) -> Dict[str, Any]:
    """Analyze customer engagement patterns"""
    message_counts = []
    for conv in conversations:
        message_count = len(conv.get("messages", []))
        if message_count > 0:
            message_counts.append(message_count)
    
    if not message_counts:
        return {"average_messages_per_conversation": 0}
    
    return {
        "average_messages_per_conversation": sum(message_counts) / len(message_counts),
        "min_messages": min(message_counts),
        "max_messages": max(message_counts),
        "total_messages": sum(message_counts)
    }

def analyze_conversion_funnel(conversations: List[Dict]) -> Dict[str, Any]:
    """Analyze the conversion funnel"""
    total = len(conversations)
    if total == 0:
        return {}
    
    stages = {
        "initiated": total,
        "engaged": sum(1 for c in conversations if len(c.get("messages", [])) > 1),
        "qualified": sum(1 for c in conversations if c.get("status") == "qualified"),
        "converted": sum(1 for c in conversations if c.get("status") == "qualified")  # Assuming qualified = converted for now
    }
    
    return {
        "stages": stages,
        "conversion_rates": {
            "engagement_rate": stages["engaged"] / stages["initiated"] if stages["initiated"] > 0 else 0,
            "qualification_rate": stages["qualified"] / stages["engaged"] if stages["engaged"] > 0 else 0,
            "overall_conversion_rate": stages["converted"] / stages["initiated"] if stages["initiated"] > 0 else 0
        }
    }

def analyze_conversation_timing(conversations: List[Dict]) -> Dict[str, Any]:
    """Analyze conversation timing patterns"""
    hour_distribution = Counter()
    day_distribution = Counter()
    
    for conv in conversations:
        created_at = conv.get("created_at")
        if created_at:
            if isinstance(created_at, str):
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                dt = created_at
            
            hour_distribution[dt.hour] += 1
            day_distribution[dt.strftime('%A')] += 1
    
    return {
        "peak_hours": dict(hour_distribution.most_common(5)),
        "peak_days": dict(day_distribution.most_common(7)),
        "hourly_distribution": dict(hour_distribution),
        "daily_distribution": dict(day_distribution)
    }

async def get_system_health_metrics() -> Dict[str, Any]:
    """Get system health metrics"""
    try:
        # Basic system health check
        health_metrics = {
            "database_connections": "healthy",
            "redis_connection": "healthy",
            "celery_workers": "unknown",  # Would need to implement worker monitoring
            "api_response_time": "unknown",  # Would need to implement API monitoring
            "memory_usage": "unknown",  # Would need to implement system monitoring
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Test database connections
        try:
            from app.core.database import async_session_maker, get_mongo_client, get_redis_client
            
            # Test PostgreSQL
            async with async_session_maker() as session:
                await session.execute("SELECT 1")
            
            # Test MongoDB
            mongo_client = get_mongo_client()
            await mongo_client.admin.command('ismaster')
            
            # Test Redis
            redis_client = get_redis_client()
            await redis_client.ping()
            
        except Exception as e:
            health_metrics["database_connections"] = f"unhealthy: {str(e)}"
        
        return health_metrics
        
    except Exception as e:
        logger.error(f"Error getting system health metrics: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

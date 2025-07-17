"""
Task Manager Service for ManipulatorAI
Coordinates and monitors asynchronous task processing
"""

from typing import Dict, Any, Optional, List
from celery import Celery
from celery.result import AsyncResult
from app.core.celery_app import celery_app
from app.tasks.conversation_tasks import (
    process_conversation_message_task,
    process_manipulator_interaction_task,
    continue_conversation_async_task,
    batch_conversation_analysis_task
)
from app.tasks.webhook_tasks import (
    process_facebook_webhook_task,
    process_google_webhook_task,
    process_generic_webhook_task,
    send_webhook_response_task
)
from app.tasks.analytics_tasks import (
    generate_conversation_analytics_task,
    generate_performance_report_task,
    cleanup_old_data_task
)
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TaskManager:
    """
    Manages asynchronous task execution and monitoring for ManipulatorAI
    """
    
    def __init__(self):
        self.celery_app = celery_app
        
        # Task queues for different priorities
        self.high_priority_queue = "conversations"
        self.medium_priority_queue = "webhooks" 
        self.low_priority_queue = "analytics"
        
        # Task tracking
        self.active_tasks = {}
    
    # Conversation Task Methods
    
    def process_customer_message_async(
        self,
        customer_id: str,
        business_id: str,
        message: str,
        message_metadata: Optional[Dict[str, Any]] = None,
        priority: str = "high"
    ) -> str:
        """
        Queue a customer message for asynchronous processing
        Returns task ID for tracking
        """
        try:
            task = process_conversation_message_task.apply_async(
                args=[customer_id, business_id, message, message_metadata],
                queue=self._get_queue_for_priority(priority)
            )
            
            self.active_tasks[task.id] = {
                "task_type": "conversation_message",
                "customer_id": customer_id,
                "business_id": business_id,
                "created_at": datetime.utcnow(),
                "priority": priority
            }
            
            logger.info(f"Queued conversation message task {task.id} for customer {customer_id}")
            return task.id
            
        except Exception as e:
            logger.error(f"Error queuing conversation message task: {e}")
            raise
    
    def process_manipulator_interaction_async(
        self,
        customer_id: str,
        business_id: str,
        interaction_data: Dict[str, Any],
        priority: str = "high"
    ) -> str:
        """
        Queue a manipulator interaction for asynchronous processing
        Returns task ID for tracking
        """
        try:
            task = process_manipulator_interaction_task.apply_async(
                args=[customer_id, business_id, interaction_data],
                queue=self._get_queue_for_priority(priority)
            )
            
            self.active_tasks[task.id] = {
                "task_type": "manipulator_interaction",
                "customer_id": customer_id,
                "business_id": business_id,
                "interaction_type": interaction_data.get("type", "unknown"),
                "created_at": datetime.utcnow(),
                "priority": priority
            }
            
            logger.info(f"Queued manipulator interaction task {task.id} for customer {customer_id}")
            return task.id
            
        except Exception as e:
            logger.error(f"Error queuing manipulator interaction task: {e}")
            raise
    
    def continue_conversation_async(
        self,
        conversation_id: str,
        customer_message: str,
        customer_context: Optional[Dict[str, Any]] = None,
        priority: str = "high"
    ) -> str:
        """
        Queue conversation continuation for asynchronous processing
        Returns task ID for tracking
        """
        try:
            task = continue_conversation_async_task.apply_async(
                args=[conversation_id, customer_message, customer_context],
                queue=self._get_queue_for_priority(priority)
            )
            
            self.active_tasks[task.id] = {
                "task_type": "continue_conversation",
                "conversation_id": conversation_id,
                "created_at": datetime.utcnow(),
                "priority": priority
            }
            
            logger.info(f"Queued conversation continuation task {task.id} for conversation {conversation_id}")
            return task.id
            
        except Exception as e:
            logger.error(f"Error queuing conversation continuation task: {e}")
            raise
    
    # Webhook Task Methods
    
    def process_webhook_async(
        self,
        webhook_data: Dict[str, Any],
        platform: str = "generic",
        priority: str = "medium"
    ) -> str:
        """
        Queue webhook processing for asynchronous handling
        Returns task ID for tracking
        """
        try:
            # Choose appropriate webhook processor based on platform
            if platform.lower() == "facebook":
                task = process_facebook_webhook_task.apply_async(
                    args=[webhook_data],
                    queue=self._get_queue_for_priority(priority)
                )
            elif platform.lower() == "google":
                task = process_google_webhook_task.apply_async(
                    args=[webhook_data],
                    queue=self._get_queue_for_priority(priority)
                )
            else:
                task = process_generic_webhook_task.apply_async(
                    args=[webhook_data, platform],
                    queue=self._get_queue_for_priority(priority)
                )
            
            self.active_tasks[task.id] = {
                "task_type": "webhook_processing",
                "platform": platform,
                "created_at": datetime.utcnow(),
                "priority": priority
            }
            
            logger.info(f"Queued webhook processing task {task.id} for platform {platform}")
            return task.id
            
        except Exception as e:
            logger.error(f"Error queuing webhook processing task: {e}")
            raise
    
    # Analytics Task Methods
    
    def generate_analytics_async(
        self,
        start_date: str,
        end_date: str,
        business_id: Optional[str] = None,
        priority: str = "low"
    ) -> str:
        """
        Queue analytics generation for asynchronous processing
        Returns task ID for tracking
        """
        try:
            task = generate_conversation_analytics_task.apply_async(
                args=[start_date, end_date, business_id],
                queue=self._get_queue_for_priority(priority)
            )
            
            self.active_tasks[task.id] = {
                "task_type": "analytics_generation",
                "start_date": start_date,
                "end_date": end_date,
                "business_id": business_id,
                "created_at": datetime.utcnow(),
                "priority": priority
            }
            
            logger.info(f"Queued analytics generation task {task.id}")
            return task.id
            
        except Exception as e:
            logger.error(f"Error queuing analytics generation task: {e}")
            raise
    
    def generate_performance_report_async(
        self,
        report_type: str = "daily",
        priority: str = "low"
    ) -> str:
        """
        Queue performance report generation
        Returns task ID for tracking
        """
        try:
            task = generate_performance_report_task.apply_async(
                args=[report_type],
                queue=self._get_queue_for_priority(priority)
            )
            
            self.active_tasks[task.id] = {
                "task_type": "performance_report",
                "report_type": report_type,
                "created_at": datetime.utcnow(),
                "priority": priority
            }
            
            logger.info(f"Queued performance report task {task.id}")
            return task.id
            
        except Exception as e:
            logger.error(f"Error queuing performance report task: {e}")
            raise
    
    # Task Status and Monitoring Methods
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific task
        """
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            
            status_info = {
                "task_id": task_id,
                "status": result.state,
                "result": result.result if result.successful() else None,
                "info": result.info if result.state == "PENDING" else result.result,
                "traceback": result.traceback if result.failed() else None,
                "created_at": self.active_tasks.get(task_id, {}).get("created_at"),
                "task_metadata": self.active_tasks.get(task_id, {})
            }
            
            # Add timing information if available
            if result.successful() and hasattr(result.result, 'get'):
                if isinstance(result.result, dict):
                    status_info["completed_at"] = result.result.get("completed_at")
                    status_info["duration"] = self._calculate_duration(
                        status_info.get("created_at"),
                        status_info.get("completed_at")
                    )
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting task status for {task_id}: {e}")
            return {
                "task_id": task_id,
                "status": "ERROR",
                "error": str(e)
            }
    
    def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        Get the result of a completed task
        """
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            
            if timeout:
                return result.get(timeout=timeout)
            else:
                return result.result if result.ready() else None
                
        except Exception as e:
            logger.error(f"Error getting task result for {task_id}: {e}")
            return None
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending or running task
        """
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            result.revoke(terminate=True)
            
            # Remove from active tasks tracking
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            logger.info(f"Cancelled task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {e}")
            return False
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of all active tasks
        """
        try:
            active_tasks = []
            
            # Clean up old tasks first
            self._cleanup_old_task_tracking()
            
            for task_id, metadata in self.active_tasks.items():
                status = self.get_task_status(task_id)
                if status["status"] not in ["SUCCESS", "FAILURE", "REVOKED"]:
                    active_tasks.append(status)
            
            return active_tasks
            
        except Exception as e:
            logger.error(f"Error getting active tasks: {e}")
            return []
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get statistics about task queues
        """
        try:
            inspect = self.celery_app.control.inspect()
            
            # Get active tasks per worker
            active_tasks = inspect.active()
            
            # Get queue lengths (this requires specific broker support)
            queue_stats = {
                "active_tasks_by_worker": active_tasks,
                "total_active_tasks": sum(len(tasks) for tasks in (active_tasks or {}).values()),
                "queues": {
                    "conversations": {"pending": 0, "active": 0},
                    "webhooks": {"pending": 0, "active": 0},
                    "analytics": {"pending": 0, "active": 0}
                }
            }
            
            # Count active tasks by queue
            for worker_tasks in (active_tasks or {}).values():
                for task in worker_tasks:
                    queue = task.get("delivery_info", {}).get("routing_key", "default")
                    if queue in queue_stats["queues"]:
                        queue_stats["queues"][queue]["active"] += 1
            
            return queue_stats
            
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            return {"error": str(e)}
    
    def schedule_cleanup_task(self, days_to_keep: int = 90) -> str:
        """
        Schedule a data cleanup task
        """
        try:
            task = cleanup_old_data_task.apply_async(
                args=[days_to_keep],
                queue=self.low_priority_queue
            )
            
            self.active_tasks[task.id] = {
                "task_type": "data_cleanup",
                "days_to_keep": days_to_keep,
                "created_at": datetime.utcnow(),
                "priority": "low"
            }
            
            logger.info(f"Scheduled cleanup task {task.id}")
            return task.id
            
        except Exception as e:
            logger.error(f"Error scheduling cleanup task: {e}")
            raise
    
    # Helper Methods
    
    def _get_queue_for_priority(self, priority: str) -> str:
        """Get queue name based on priority"""
        queue_map = {
            "high": self.high_priority_queue,
            "medium": self.medium_priority_queue,
            "low": self.low_priority_queue
        }
        return queue_map.get(priority, self.medium_priority_queue)
    
    def _calculate_duration(self, start_time, end_time) -> Optional[float]:
        """Calculate duration between two timestamps"""
        try:
            if start_time and end_time:
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                
                return (end_time - start_time).total_seconds()
            return None
        except Exception:
            return None
    
    def _cleanup_old_task_tracking(self):
        """Clean up old task tracking data"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            tasks_to_remove = []
            for task_id, metadata in self.active_tasks.items():
                created_at = metadata.get("created_at")
                if created_at and created_at < cutoff_time:
                    # Check if task is actually complete
                    result = AsyncResult(task_id, app=self.celery_app)
                    if result.state in ["SUCCESS", "FAILURE", "REVOKED"]:
                        tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self.active_tasks[task_id]
                
            if tasks_to_remove:
                logger.info(f"Cleaned up {len(tasks_to_remove)} old task tracking entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up old task tracking: {e}")
    
    # Alias methods for validation compatibility
    def process_conversation_async(self, conversation_data: dict, priority: str = "high") -> str:
        """Alias for process_customer_message_async for validation compatibility"""
        return self.process_customer_message_async(
            conversation_id=conversation_data.get("conversation_id"),
            customer_message=conversation_data.get("message", ""),
            customer_id=conversation_data.get("customer_id"),
            metadata=conversation_data.get("metadata", {}),
            priority=priority
        )
    
    def get_queue_statistics(self) -> Dict[str, Any]:
        """Alias for get_queue_stats for validation compatibility"""
        return self.get_queue_stats()


# Global task manager instance
task_manager = TaskManager()

"""
Celery Configuration for ManipulatorAI
Handles asynchronous task processing with Redis as message broker
"""

from celery import Celery
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_celery_app() -> Celery:
    """
    Create and configure Celery application for async task processing
    """
    
    # Initialize Celery with Redis as broker and backend
    celery_app = Celery(
        "manipulator_ai",
        broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        include=[
            "app.tasks.conversation_tasks",
            "app.tasks.webhook_tasks", 
            "app.tasks.analytics_tasks"
        ]
    )
    
    # Configure Celery settings
    celery_app.conf.update(
        # Task serialization
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        
        # Task routing and execution
        task_routes={
            "app.tasks.conversation_tasks.*": {"queue": "conversations"},
            "app.tasks.webhook_tasks.*": {"queue": "webhooks"},
            "app.tasks.analytics_tasks.*": {"queue": "analytics"}
        },
        
        # Task timeouts and retries
        task_time_limit=300,  # 5 minutes max
        task_soft_time_limit=240,  # 4 minutes soft limit
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        
        # Result backend settings
        result_expires=3600,  # 1 hour
        result_persistent=True,
        
        # Worker settings
        worker_max_tasks_per_child=1000,
        worker_disable_rate_limits=False,
        
        # Monitoring
        worker_send_task_events=True,
        task_send_sent_event=True,
        
        # Queue configuration
        task_default_queue="default",
        task_create_missing_queues=True,
        
        # Error handling
        task_reject_on_worker_lost=True,
        task_ignore_result=False
    )
    
    return celery_app

# Create the Celery app instance
celery_app = create_celery_app()

# Health check task
@celery_app.task(name="health_check")
def health_check():
    """Simple health check task for monitoring Celery workers"""
    return {"status": "healthy", "timestamp": "2025-07-15T12:00:00Z"}

if __name__ == "__main__":
    # Start Celery worker
    celery_app.start()

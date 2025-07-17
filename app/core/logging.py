"""
Comprehensive Logging Configuration for ManipulatorAI
Provides structured logging with different levels and outputs
"""

import logging
import logging.handlers
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import json


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'conversation_id'):
            log_entry["conversation_id"] = record.conversation_id
        if hasattr(record, 'task_id'):
            log_entry["task_id"] = record.task_id
        if hasattr(record, 'duration'):
            log_entry["duration"] = record.duration
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        
        return json.dumps(log_entry)


class LoggerManager:
    """
    Centralized logger management for the application
    """
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self._configure_loggers()
    
    def _configure_loggers(self):
        """Configure all application loggers"""
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # File handler for general application logs
        app_log_file = self.log_dir / "app.log"
        app_file_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        app_file_handler.setFormatter(JSONFormatter())
        app_file_handler.setLevel(logging.INFO)
        
        # Error log file handler
        error_log_file = self.log_dir / "error.log"
        error_file_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_file_handler.setFormatter(JSONFormatter())
        error_file_handler.setLevel(logging.ERROR)
        
        # Add handlers to root logger
        root_logger.addHandler(console_handler)
        root_logger.addHandler(app_file_handler)
        root_logger.addHandler(error_file_handler)
        
        # Configure specific loggers
        self._configure_api_logger()
        self._configure_task_logger()
        self._configure_conversation_logger()
        self._configure_performance_logger()
    
    def _configure_api_logger(self):
        """Configure API request/response logging"""
        api_logger = logging.getLogger("api")
        
        api_log_file = self.log_dir / "api.log"
        api_handler = logging.handlers.RotatingFileHandler(
            api_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
        api_handler.setFormatter(JSONFormatter())
        api_handler.setLevel(logging.INFO)
        
        api_logger.addHandler(api_handler)
        api_logger.setLevel(logging.INFO)
        api_logger.propagate = False  # Don't propagate to root logger
    
    def _configure_task_logger(self):
        """Configure Celery task logging"""
        task_logger = logging.getLogger("tasks")
        
        task_log_file = self.log_dir / "tasks.log"
        task_handler = logging.handlers.RotatingFileHandler(
            task_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
        task_handler.setFormatter(JSONFormatter())
        task_handler.setLevel(logging.INFO)
        
        task_logger.addHandler(task_handler)
        task_logger.setLevel(logging.INFO)
        task_logger.propagate = False
    
    def _configure_conversation_logger(self):
        """Configure conversation flow logging"""
        conv_logger = logging.getLogger("conversation")
        
        conv_log_file = self.log_dir / "conversations.log"
        conv_handler = logging.handlers.RotatingFileHandler(
            conv_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=15
        )
        conv_handler.setFormatter(JSONFormatter())
        conv_handler.setLevel(logging.INFO)
        
        conv_logger.addHandler(conv_handler)
        conv_logger.setLevel(logging.INFO)
        conv_logger.propagate = False
    
    def _configure_performance_logger(self):
        """Configure performance metrics logging"""
        perf_logger = logging.getLogger("performance")
        
        perf_log_file = self.log_dir / "performance.log"
        perf_handler = logging.handlers.RotatingFileHandler(
            perf_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=20
        )
        perf_handler.setFormatter(JSONFormatter())
        perf_handler.setLevel(logging.INFO)
        
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.INFO)
        perf_logger.propagate = False
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a configured logger by name"""
        return logging.getLogger(name)
    
    @staticmethod
    def log_api_request(endpoint: str, method: str, user_id: Optional[str] = None, 
                       status_code: Optional[int] = None, duration: Optional[float] = None):
        """Log API request details"""
        logger = logging.getLogger("api")
        extra = {
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "status_code": status_code,
            "duration": duration
        }
        logger.info(f"{method} {endpoint}", extra=extra)
    
    @staticmethod
    def log_task_execution(task_name: str, task_id: str, status: str, 
                          duration: Optional[float] = None, error: Optional[str] = None):
        """Log task execution details"""
        logger = logging.getLogger("tasks")
        extra = {
            "task_name": task_name,
            "task_id": task_id,
            "status": status,
            "duration": duration,
            "error": error
        }
        logger.info(f"Task {task_name} {status}", extra=extra)
    
    @staticmethod
    def log_conversation_event(conversation_id: str, event_type: str, 
                              customer_id: Optional[str] = None, 
                              message_length: Optional[int] = None):
        """Log conversation events"""
        logger = logging.getLogger("conversation")
        extra = {
            "conversation_id": conversation_id,
            "event_type": event_type,
            "customer_id": customer_id,
            "message_length": message_length
        }
        logger.info(f"Conversation {event_type}", extra=extra)
    
    @staticmethod
    def log_performance_metric(metric_name: str, value: float, unit: str = "ms"):
        """Log performance metrics"""
        logger = logging.getLogger("performance")
        extra = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit
        }
        logger.info(f"Performance metric: {metric_name} = {value}{unit}", extra=extra)


# Initialize logging on import
logger_manager = LoggerManager()

# Export commonly used loggers
api_logger = logger_manager.get_logger("api")
task_logger = logger_manager.get_logger("tasks")
conversation_logger = logger_manager.get_logger("conversation")
performance_logger = logger_manager.get_logger("performance")
main_logger = logger_manager.get_logger("main")

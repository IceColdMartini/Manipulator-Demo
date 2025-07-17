"""
Comprehensive Error Handling for ManipulatorAI
Provides custom exceptions, error handlers, and recovery mechanisms
"""

import traceback
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import asyncio

from app.core.logging import main_logger as logger


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    CONVERSATION = "conversation"
    TASK_PROCESSING = "task_processing"
    SYSTEM = "system"


class ManipulatorAIException(Exception):
    """Base exception class for ManipulatorAI application"""
    
    def __init__(
        self, 
        message: str,
        error_code: str = "GENERAL_ERROR",
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = True
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp.isoformat()
        }


class ConversationError(ManipulatorAIException):
    """Conversation-related errors"""
    
    def __init__(self, message: str, conversation_id: Optional[str] = None, **kwargs):
        super().__init__(
            message, 
            error_code="CONVERSATION_ERROR",
            category=ErrorCategory.CONVERSATION,
            **kwargs
        )
        if conversation_id:
            self.details["conversation_id"] = conversation_id


class DatabaseError(ManipulatorAIException):
    """Database-related errors"""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="DATABASE_ERROR", 
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        if operation:
            self.details["operation"] = operation


class ExternalAPIError(ManipulatorAIException):
    """External API integration errors"""
    
    def __init__(self, message: str, service: Optional[str] = None, 
                 status_code: Optional[int] = None, **kwargs):
        super().__init__(
            message,
            error_code="EXTERNAL_API_ERROR",
            category=ErrorCategory.EXTERNAL_API,
            **kwargs
        )
        if service:
            self.details["service"] = service
        if status_code:
            self.details["status_code"] = status_code


class TaskProcessingError(ManipulatorAIException):
    """Task processing errors"""
    
    def __init__(self, message: str, task_id: Optional[str] = None, 
                 task_name: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="TASK_PROCESSING_ERROR",
            category=ErrorCategory.TASK_PROCESSING,
            **kwargs
        )
        if task_id:
            self.details["task_id"] = task_id
        if task_name:
            self.details["task_name"] = task_name


class ValidationError(ManipulatorAIException):
    """Input validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, **kwargs):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["value"] = str(value)


class ErrorHandler:
    """Centralized error handling and recovery"""
    
    def __init__(self):
        self.error_counts = {}
        self.recovery_strategies = {}
        self._register_recovery_strategies()
    
    def _register_recovery_strategies(self):
        """Register recovery strategies for different error types"""
        self.recovery_strategies = {
            ErrorCategory.DATABASE: self._recover_database_error,
            ErrorCategory.EXTERNAL_API: self._recover_external_api_error,
            ErrorCategory.TASK_PROCESSING: self._recover_task_processing_error,
            ErrorCategory.CONVERSATION: self._recover_conversation_error
        }
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle an error with logging, recovery, and response generation
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            Error response dictionary
        """
        context = context or {}
        
        # Convert to ManipulatorAI exception if needed
        if not isinstance(error, ManipulatorAIException):
            error = self._convert_to_manipulator_error(error)
        
        # Log the error
        self._log_error(error, context)
        
        # Update error counts
        self._update_error_counts(error)
        
        # Attempt recovery if error is recoverable
        recovery_result = None
        if error.recoverable:
            recovery_result = await self._attempt_recovery(error, context)
        
        # Generate error response
        response = self._generate_error_response(error, recovery_result)
        
        return response
    
    def _convert_to_manipulator_error(self, error: Exception) -> ManipulatorAIException:
        """Convert generic exceptions to ManipulatorAI exceptions"""
        if isinstance(error, HTTPException):
            return ValidationError(
                message=str(error.detail),
                details={"status_code": error.status_code}
            )
        elif isinstance(error, asyncio.TimeoutError):
            return ExternalAPIError(
                message="Operation timed out",
                severity=ErrorSeverity.HIGH
            )
        elif isinstance(error, ConnectionError):
            return DatabaseError(
                message="Connection error occurred",
                severity=ErrorSeverity.HIGH
            )
        else:
            return ManipulatorAIException(
                message=str(error),
                error_code="UNKNOWN_ERROR",
                severity=ErrorSeverity.MEDIUM,
                details={"original_type": type(error).__name__}
            )
    
    def _log_error(self, error: ManipulatorAIException, context: Dict[str, Any]):
        """Log error with appropriate severity level"""
        log_data = error.to_dict()
        log_data.update(context)
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(f"HIGH SEVERITY ERROR: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"MEDIUM SEVERITY ERROR: {error.message}", extra=log_data)
        else:
            logger.info(f"LOW SEVERITY ERROR: {error.message}", extra=log_data)
    
    def _update_error_counts(self, error: ManipulatorAIException):
        """Update error statistics"""
        key = f"{error.category.value}:{error.error_code}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    async def _attempt_recovery(self, error: ManipulatorAIException, 
                               context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt to recover from error using registered strategies"""
        recovery_strategy = self.recovery_strategies.get(error.category)
        
        if recovery_strategy:
            try:
                return await recovery_strategy(error, context)
            except Exception as recovery_error:
                logger.error(f"Recovery failed: {recovery_error}")
                return None
        
        return None
    
    async def _recover_database_error(self, error: DatabaseError, 
                                    context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt recovery from database errors"""
        # Could implement connection retry, failover, etc.
        logger.info("Attempting database error recovery")
        return {"recovery_attempted": True, "strategy": "database_retry"}
    
    async def _recover_external_api_error(self, error: ExternalAPIError, 
                                        context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt recovery from external API errors"""
        # Could implement retry with backoff, fallback service, etc.
        logger.info("Attempting external API error recovery")
        return {"recovery_attempted": True, "strategy": "api_retry"}
    
    async def _recover_task_processing_error(self, error: TaskProcessingError, 
                                           context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt recovery from task processing errors"""
        # Could implement task retry, alternative queue, etc.
        logger.info("Attempting task processing error recovery")
        return {"recovery_attempted": True, "strategy": "task_retry"}
    
    async def _recover_conversation_error(self, error: ConversationError, 
                                        context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt recovery from conversation errors"""
        # Could implement conversation reset, fallback response, etc.
        logger.info("Attempting conversation error recovery")
        return {"recovery_attempted": True, "strategy": "conversation_fallback"}
    
    def _generate_error_response(self, error: ManipulatorAIException, 
                               recovery_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate standardized error response"""
        response = {
            "success": False,
            "error": {
                "code": error.error_code,
                "message": error.message,
                "category": error.category.value,
                "severity": error.severity.value,
                "timestamp": error.timestamp.isoformat(),
                "recoverable": error.recoverable
            }
        }
        
        if error.details:
            response["error"]["details"] = error.details
        
        if recovery_result:
            response["recovery"] = recovery_result
        
        return response
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        return {
            "error_counts": self.error_counts.copy(),
            "total_errors": sum(self.error_counts.values()),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global error handler instance
error_handler = ErrorHandler()


# FastAPI exception handlers
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors"""
    response = await error_handler.handle_error(exc, {"endpoint": str(request.url)})
    return JSONResponse(
        status_code=400,
        content=response
    )


async def conversation_exception_handler(request: Request, exc: ConversationError):
    """Handle conversation errors"""
    response = await error_handler.handle_error(exc, {"endpoint": str(request.url)})
    return JSONResponse(
        status_code=422,
        content=response
    )


async def database_exception_handler(request: Request, exc: DatabaseError):
    """Handle database errors"""
    response = await error_handler.handle_error(exc, {"endpoint": str(request.url)})
    return JSONResponse(
        status_code=500,
        content=response
    )


async def external_api_exception_handler(request: Request, exc: ExternalAPIError):
    """Handle external API errors"""
    response = await error_handler.handle_error(exc, {"endpoint": str(request.url)})
    return JSONResponse(
        status_code=502,
        content=response
    )


async def task_processing_exception_handler(request: Request, exc: TaskProcessingError):
    """Handle task processing errors"""
    response = await error_handler.handle_error(exc, {"endpoint": str(request.url)})
    return JSONResponse(
        status_code=500,
        content=response
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    response = await error_handler.handle_error(exc, {"endpoint": str(request.url)})
    return JSONResponse(
        status_code=500,
        content=response
    )


# Decorator for automatic error handling
def handle_errors(func: Callable) -> Callable:
    """Decorator to automatically handle errors in functions"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ManipulatorAIException:
            raise  # Re-raise custom exceptions
        except Exception as e:
            # Convert and raise as ManipulatorAI exception
            manipulator_error = error_handler._convert_to_manipulator_error(e)
            raise manipulator_error
    
    return wrapper

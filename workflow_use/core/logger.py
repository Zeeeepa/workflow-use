"""
Advanced logging configuration for Workflow-Use Suite.

Provides structured logging with multiple outputs, performance tracking,
and integration with monitoring systems.
"""

import sys
import json
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, Union
from contextvars import ContextVar

from loguru import logger
from rich.console import Console
from rich.traceback import install as install_rich_traceback

from workflow_use.core.config import get_settings


# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
workflow_id_var: ContextVar[Optional[str]] = ContextVar("workflow_id", default=None)


class StructuredFormatter:
    """Custom formatter for structured JSON logging."""
    
    def __init__(self, include_extra: bool = True):
        """Initialize structured formatter.
        
        Args:
            include_extra: Whether to include extra fields in log records
        """
        self.include_extra = include_extra
    
    def format(self, record: Dict[str, Any]) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record dictionary
            
        Returns:
            JSON formatted log string
        """
        # Base log data
        log_data = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "message": record["message"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }
        
        # Add context variables
        if request_id := request_id_var.get():
            log_data["request_id"] = request_id
        if user_id := user_id_var.get():
            log_data["user_id"] = user_id
        if workflow_id := workflow_id_var.get():
            log_data["workflow_id"] = workflow_id
        
        # Add exception information
        if record.get("exception"):
            exc_info = record["exception"]
            log_data["exception"] = {
                "type": exc_info.type.__name__ if exc_info.type else None,
                "value": str(exc_info.value) if exc_info.value else None,
                "traceback": exc_info.traceback.format() if exc_info.traceback else None,
            }
        
        # Add extra fields
        if self.include_extra and "extra" in record:
            log_data.update(record["extra"])
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class PerformanceLogger:
    """Logger for performance metrics and timing."""
    
    def __init__(self, logger_name: str = "performance"):
        """Initialize performance logger.
        
        Args:
            logger_name: Name of the logger instance
        """
        self.logger = get_logger(logger_name)
    
    def log_timing(
        self,
        operation: str,
        duration_ms: float,
        **extra_data: Any
    ) -> None:
        """Log operation timing.
        
        Args:
            operation: Name of the operation
            duration_ms: Duration in milliseconds
            **extra_data: Additional data to include
        """
        self.logger.info(
            f"Performance: {operation} completed in {duration_ms:.2f}ms",
            operation=operation,
            duration_ms=duration_ms,
            **extra_data
        )
    
    def log_memory_usage(
        self,
        operation: str,
        memory_mb: float,
        **extra_data: Any
    ) -> None:
        """Log memory usage.
        
        Args:
            operation: Name of the operation
            memory_mb: Memory usage in MB
            **extra_data: Additional data to include
        """
        self.logger.info(
            f"Memory: {operation} used {memory_mb:.2f}MB",
            operation=operation,
            memory_mb=memory_mb,
            **extra_data
        )


class AuditLogger:
    """Logger for audit trails and security events."""
    
    def __init__(self, logger_name: str = "audit"):
        """Initialize audit logger.
        
        Args:
            logger_name: Name of the logger instance
        """
        self.logger = get_logger(logger_name)
    
    def log_user_action(
        self,
        user_id: str,
        action: str,
        resource: Optional[str] = None,
        **extra_data: Any
    ) -> None:
        """Log user action for audit trail.
        
        Args:
            user_id: ID of the user performing the action
            action: Action being performed
            resource: Resource being acted upon
            **extra_data: Additional audit data
        """
        self.logger.info(
            f"User action: {user_id} performed {action}",
            user_id=user_id,
            action=action,
            resource=resource,
            **extra_data
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        **extra_data: Any
    ) -> None:
        """Log security event.
        
        Args:
            event_type: Type of security event
            severity: Severity level (low, medium, high, critical)
            description: Event description
            **extra_data: Additional security data
        """
        log_method = getattr(self.logger, severity.lower(), self.logger.warning)
        log_method(
            f"Security event: {event_type} - {description}",
            event_type=event_type,
            severity=severity,
            **extra_data
        )


def setup_logging() -> None:
    """Setup logging configuration based on settings."""
    settings = get_settings()
    
    # Remove default logger
    logger.remove()
    
    # Install rich traceback for better error display
    install_rich_traceback(show_locals=settings.debug)
    
    # Console handler
    if settings.logging.json_logs:
        # JSON structured logging
        logger.add(
            sys.stderr,
            format=StructuredFormatter().format,
            level=settings.logging.level,
            colorize=False,
            backtrace=settings.debug,
            diagnose=settings.debug,
        )
    else:
        # Human-readable logging
        logger.add(
            sys.stderr,
            format=settings.logging.format,
            level=settings.logging.level,
            colorize=True,
            backtrace=settings.debug,
            diagnose=settings.debug,
        )
    
    # File handler
    if settings.logging.file_path:
        logger.add(
            settings.logging.file_path,
            format=StructuredFormatter().format if settings.logging.json_logs else settings.logging.format,
            level=settings.logging.level,
            rotation=settings.logging.file_rotation,
            retention=settings.logging.file_retention,
            compression="gz",
            backtrace=settings.debug,
            diagnose=settings.debug,
        )
    
    # Performance logging file
    if settings.monitoring.performance_tracking:
        perf_log_path = settings.logs_dir / "performance.log"
        logger.add(
            perf_log_path,
            format=StructuredFormatter().format,
            level="INFO",
            filter=lambda record: record["name"] == "performance",
            rotation="100 MB",
            retention="7 days",
            compression="gz",
        )
    
    # Audit logging file
    audit_log_path = settings.logs_dir / "audit.log"
    logger.add(
        audit_log_path,
        format=StructuredFormatter().format,
        level="INFO",
        filter=lambda record: record["name"] == "audit",
        rotation="100 MB",
        retention="30 days",
        compression="gz",
    )
    
    # Error logging file
    error_log_path = settings.logs_dir / "errors.log"
    logger.add(
        error_log_path,
        format=StructuredFormatter().format,
        level="ERROR",
        rotation="50 MB",
        retention="30 days",
        compression="gz",
    )


def get_logger(name: str) -> Any:
    """Get logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    workflow_id: Optional[str] = None
) -> None:
    """Set request context for logging.
    
    Args:
        request_id: Unique request identifier
        user_id: User identifier
        workflow_id: Workflow identifier
    """
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if workflow_id:
        workflow_id_var.set(workflow_id)


def clear_request_context() -> None:
    """Clear request context."""
    request_id_var.set(None)
    user_id_var.set(None)
    workflow_id_var.set(None)


def log_exception(
    exc: Exception,
    logger_instance: Optional[Any] = None,
    message: Optional[str] = None,
    **extra_data: Any
) -> None:
    """Log exception with full context.
    
    Args:
        exc: Exception to log
        logger_instance: Logger instance to use
        message: Custom message
        **extra_data: Additional data to include
    """
    if logger_instance is None:
        logger_instance = get_logger("exception")
    
    error_message = message or f"Exception occurred: {exc}"
    
    # Add exception details to extra data
    extra_data.update({
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "traceback": traceback.format_exc(),
    })
    
    logger_instance.error(error_message, **extra_data)


def log_workflow_event(
    workflow_id: str,
    event_type: str,
    message: str,
    **extra_data: Any
) -> None:
    """Log workflow-specific event.
    
    Args:
        workflow_id: Workflow identifier
        event_type: Type of event (start, step, complete, error)
        message: Event message
        **extra_data: Additional event data
    """
    workflow_logger = get_logger("workflow")
    
    # Set workflow context
    old_workflow_id = workflow_id_var.get()
    workflow_id_var.set(workflow_id)
    
    try:
        workflow_logger.info(
            message,
            workflow_id=workflow_id,
            event_type=event_type,
            **extra_data
        )
    finally:
        # Restore previous context
        workflow_id_var.set(old_workflow_id)


def log_browser_event(
    action: str,
    url: Optional[str] = None,
    element: Optional[str] = None,
    success: bool = True,
    **extra_data: Any
) -> None:
    """Log browser automation event.
    
    Args:
        action: Browser action performed
        url: URL where action was performed
        element: Element selector or description
        success: Whether the action was successful
        **extra_data: Additional browser data
    """
    browser_logger = get_logger("browser")
    
    level = "info" if success else "warning"
    status = "succeeded" if success else "failed"
    
    message = f"Browser action {action} {status}"
    if url:
        message += f" on {url}"
    if element:
        message += f" for element {element}"
    
    getattr(browser_logger, level)(
        message,
        action=action,
        url=url,
        element=element,
        success=success,
        **extra_data
    )


# Initialize logging on module import
setup_logging()

# Create commonly used logger instances
main_logger = get_logger("main")
performance_logger = PerformanceLogger()
audit_logger = AuditLogger()


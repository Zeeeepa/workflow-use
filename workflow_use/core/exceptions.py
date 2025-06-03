"""
Custom exceptions for Workflow-Use Suite.

Provides a comprehensive hierarchy of exceptions for different error scenarios
with proper error codes, messages, and context information.
"""

from typing import Any, Dict, Optional


class WorkflowError(Exception):
    """Base exception for all workflow-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """Initialize workflow error.
        
        Args:
            message: Error message
            error_code: Unique error code for categorization
            context: Additional context information
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "WORKFLOW_ERROR"
        self.context = context or {}
        self.cause = cause
    
    def __str__(self) -> str:
        """String representation of the error."""
        parts = [f"[{self.error_code}] {self.message}"]
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        
        return " | ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None
        }


class ConfigError(WorkflowError):
    """Configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        """Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            **kwargs: Additional arguments for WorkflowError
        """
        context = kwargs.get("context", {})
        if config_key:
            context["config_key"] = config_key
        
        super().__init__(
            message,
            error_code="CONFIG_ERROR",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class ValidationError(WorkflowError):
    """Data validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        """Initialize validation error.
        
        Args:
            message: Error message
            field: Field name that failed validation
            value: Invalid value
            **kwargs: Additional arguments for WorkflowError
        """
        context = kwargs.get("context", {})
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)
        
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class BrowserError(WorkflowError):
    """Browser automation errors."""
    
    def __init__(
        self,
        message: str,
        browser_type: Optional[str] = None,
        page_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize browser error.
        
        Args:
            message: Error message
            browser_type: Type of browser (chrome, firefox, etc.)
            page_url: URL of the page where error occurred
            **kwargs: Additional arguments for WorkflowError
        """
        context = kwargs.get("context", {})
        if browser_type:
            context["browser_type"] = browser_type
        if page_url:
            context["page_url"] = page_url
        
        super().__init__(
            message,
            error_code="BROWSER_ERROR",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class BrowserTimeoutError(BrowserError):
    """Browser operation timeout errors."""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """Initialize browser timeout error.
        
        Args:
            message: Error message
            timeout_seconds: Timeout duration in seconds
            operation: Operation that timed out
            **kwargs: Additional arguments for BrowserError
        """
        context = kwargs.get("context", {})
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        if operation:
            context["operation"] = operation
        
        super().__init__(
            message,
            error_code="BROWSER_TIMEOUT",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class ElementNotFoundError(BrowserError):
    """Element not found in browser page."""
    
    def __init__(
        self,
        message: str,
        selector: Optional[str] = None,
        element_type: Optional[str] = None,
        **kwargs
    ):
        """Initialize element not found error.
        
        Args:
            message: Error message
            selector: CSS/XPath selector used to find element
            element_type: Type of element (button, input, etc.)
            **kwargs: Additional arguments for BrowserError
        """
        context = kwargs.get("context", {})
        if selector:
            context["selector"] = selector
        if element_type:
            context["element_type"] = element_type
        
        super().__init__(
            message,
            error_code="ELEMENT_NOT_FOUND",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class WorkflowExecutionError(WorkflowError):
    """Workflow execution errors."""
    
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        step_id: Optional[str] = None,
        step_name: Optional[str] = None,
        **kwargs
    ):
        """Initialize workflow execution error.
        
        Args:
            message: Error message
            workflow_id: ID of the workflow
            step_id: ID of the step that failed
            step_name: Name of the step that failed
            **kwargs: Additional arguments for WorkflowError
        """
        context = kwargs.get("context", {})
        if workflow_id:
            context["workflow_id"] = workflow_id
        if step_id:
            context["step_id"] = step_id
        if step_name:
            context["step_name"] = step_name
        
        super().__init__(
            message,
            error_code="WORKFLOW_EXECUTION_ERROR",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class WorkflowNotFoundError(WorkflowError):
    """Workflow not found error."""
    
    def __init__(self, workflow_id: str, **kwargs):
        """Initialize workflow not found error.
        
        Args:
            workflow_id: ID of the workflow that was not found
            **kwargs: Additional arguments for WorkflowError
        """
        message = f"Workflow with ID '{workflow_id}' not found"
        context = kwargs.get("context", {})
        context["workflow_id"] = workflow_id
        
        super().__init__(
            message,
            error_code="WORKFLOW_NOT_FOUND",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class AIProviderError(WorkflowError):
    """AI provider errors."""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """Initialize AI provider error.
        
        Args:
            message: Error message
            provider: AI provider name (openai, anthropic, etc.)
            model: Model name that caused the error
            **kwargs: Additional arguments for WorkflowError
        """
        context = kwargs.get("context", {})
        if provider:
            context["provider"] = provider
        if model:
            context["model"] = model
        
        super().__init__(
            message,
            error_code="AI_PROVIDER_ERROR",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class AIQuotaExceededError(AIProviderError):
    """AI provider quota exceeded error."""
    
    def __init__(
        self,
        message: str,
        quota_type: Optional[str] = None,
        reset_time: Optional[str] = None,
        **kwargs
    ):
        """Initialize AI quota exceeded error.
        
        Args:
            message: Error message
            quota_type: Type of quota exceeded (requests, tokens, etc.)
            reset_time: When the quota resets
            **kwargs: Additional arguments for AIProviderError
        """
        context = kwargs.get("context", {})
        if quota_type:
            context["quota_type"] = quota_type
        if reset_time:
            context["reset_time"] = reset_time
        
        super().__init__(
            message,
            error_code="AI_QUOTA_EXCEEDED",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class DatabaseError(WorkflowError):
    """Database operation errors."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        """Initialize database error.
        
        Args:
            message: Error message
            operation: Database operation (select, insert, update, delete)
            table: Table name where error occurred
            **kwargs: Additional arguments for WorkflowError
        """
        context = kwargs.get("context", {})
        if operation:
            context["operation"] = operation
        if table:
            context["table"] = table
        
        super().__init__(
            message,
            error_code="DATABASE_ERROR",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class AuthenticationError(WorkflowError):
    """Authentication and authorization errors."""
    
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        **kwargs
    ):
        """Initialize authentication error.
        
        Args:
            message: Error message
            user_id: User ID that failed authentication
            resource: Resource that was being accessed
            **kwargs: Additional arguments for WorkflowError
        """
        context = kwargs.get("context", {})
        if user_id:
            context["user_id"] = user_id
        if resource:
            context["resource"] = resource
        
        super().__init__(
            message,
            error_code="AUTHENTICATION_ERROR",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class RateLimitError(WorkflowError):
    """Rate limiting errors."""
    
    def __init__(
        self,
        message: str,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        """Initialize rate limit error.
        
        Args:
            message: Error message
            limit: Rate limit threshold
            window_seconds: Rate limit window in seconds
            retry_after: Seconds to wait before retrying
            **kwargs: Additional arguments for WorkflowError
        """
        context = kwargs.get("context", {})
        if limit:
            context["limit"] = limit
        if window_seconds:
            context["window_seconds"] = window_seconds
        if retry_after:
            context["retry_after"] = retry_after
        
        super().__init__(
            message,
            error_code="RATE_LIMIT_ERROR",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class NetworkError(WorkflowError):
    """Network connectivity errors."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        """Initialize network error.
        
        Args:
            message: Error message
            url: URL that caused the error
            status_code: HTTP status code
            **kwargs: Additional arguments for WorkflowError
        """
        context = kwargs.get("context", {})
        if url:
            context["url"] = url
        if status_code:
            context["status_code"] = status_code
        
        super().__init__(
            message,
            error_code="NETWORK_ERROR",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


class FileOperationError(WorkflowError):
    """File system operation errors."""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """Initialize file operation error.
        
        Args:
            message: Error message
            file_path: Path to the file
            operation: File operation (read, write, delete, etc.)
            **kwargs: Additional arguments for WorkflowError
        """
        context = kwargs.get("context", {})
        if file_path:
            context["file_path"] = file_path
        if operation:
            context["operation"] = operation
        
        super().__init__(
            message,
            error_code="FILE_OPERATION_ERROR",
            context=context,
            **{k: v for k, v in kwargs.items() if k != "context"}
        )


# Exception mapping for easy lookup
EXCEPTION_MAP = {
    "WORKFLOW_ERROR": WorkflowError,
    "CONFIG_ERROR": ConfigError,
    "VALIDATION_ERROR": ValidationError,
    "BROWSER_ERROR": BrowserError,
    "BROWSER_TIMEOUT": BrowserTimeoutError,
    "ELEMENT_NOT_FOUND": ElementNotFoundError,
    "WORKFLOW_EXECUTION_ERROR": WorkflowExecutionError,
    "WORKFLOW_NOT_FOUND": WorkflowNotFoundError,
    "AI_PROVIDER_ERROR": AIProviderError,
    "AI_QUOTA_EXCEEDED": AIQuotaExceededError,
    "DATABASE_ERROR": DatabaseError,
    "AUTHENTICATION_ERROR": AuthenticationError,
    "RATE_LIMIT_ERROR": RateLimitError,
    "NETWORK_ERROR": NetworkError,
    "FILE_OPERATION_ERROR": FileOperationError,
}


def create_exception(
    error_code: str,
    message: str,
    **kwargs
) -> WorkflowError:
    """Create exception instance from error code.
    
    Args:
        error_code: Error code to determine exception type
        message: Error message
        **kwargs: Additional arguments for the exception
    
    Returns:
        Exception instance of the appropriate type
    """
    exception_class = EXCEPTION_MAP.get(error_code, WorkflowError)
    return exception_class(message, error_code=error_code, **kwargs)


"""
Workflow-Use Suite: Enterprise-grade workflow automation with browser-use integration.

A comprehensive platform for creating, managing, and executing automated workflows
with AI-powered browser automation capabilities.
"""

__version__ = "1.0.0"
__author__ = "Workflow-Use Team"
__email__ = "team@workflow-use.com"
__license__ = "MIT"

from workflow_use.core.config import Settings
from workflow_use.core.exceptions import WorkflowError, BrowserError, ConfigError
from workflow_use.core.logger import get_logger
from workflow_use.models.workflow import Workflow, WorkflowStep, WorkflowResult
from workflow_use.services.browser import BrowserService
from workflow_use.services.workflow import WorkflowService

# Core exports
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # Core components
    "Settings",
    "get_logger",
    
    # Models
    "Workflow",
    "WorkflowStep", 
    "WorkflowResult",
    
    # Services
    "BrowserService",
    "WorkflowService",
    
    # Exceptions
    "WorkflowError",
    "BrowserError", 
    "ConfigError",
]

# Initialize default logger
logger = get_logger(__name__)
logger.info(f"Workflow-Use Suite v{__version__} initialized")


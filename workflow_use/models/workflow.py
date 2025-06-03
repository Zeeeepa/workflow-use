"""
Workflow data models with enhanced validation and type safety.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(str, Enum):
    """Types of workflow steps."""
    BROWSER_ACTION = "browser_action"
    API_CALL = "api_call"
    DATA_PROCESSING = "data_processing"
    CONDITION = "condition"
    LOOP = "loop"
    DELAY = "delay"
    NOTIFICATION = "notification"
    FILE_OPERATION = "file_operation"
    AI_TASK = "ai_task"


class WorkflowStep(BaseModel):
    """Individual step in a workflow."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    step_type: StepType
    order: int = Field(..., ge=0)
    
    # Step configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution settings
    timeout_seconds: Optional[int] = Field(None, ge=1, le=3600)
    retry_count: int = Field(default=0, ge=0, le=10)
    retry_delay_seconds: int = Field(default=1, ge=0, le=300)
    
    # Conditional execution
    condition: Optional[str] = Field(None, description="Python expression for conditional execution")
    
    # Dependencies
    depends_on: List[str] = Field(default_factory=list, description="Step IDs this step depends on")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("config")
    def validate_config(cls, v: Dict[str, Any], values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate step configuration based on step type."""
        step_type = values.get("step_type")
        
        if step_type == StepType.BROWSER_ACTION:
            required_fields = ["action", "target"]
            for field in required_fields:
                if field not in v:
                    raise ValueError(f"Browser action step requires '{field}' in config")
        
        elif step_type == StepType.API_CALL:
            required_fields = ["url", "method"]
            for field in required_fields:
                if field not in v:
                    raise ValueError(f"API call step requires '{field}' in config")
        
        elif step_type == StepType.DELAY:
            if "duration_seconds" not in v:
                raise ValueError("Delay step requires 'duration_seconds' in config")
            if not isinstance(v["duration_seconds"], (int, float)) or v["duration_seconds"] <= 0:
                raise ValueError("duration_seconds must be a positive number")
        
        return v
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class WorkflowResult(BaseModel):
    """Result of workflow execution."""
    
    workflow_id: str
    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    status: WorkflowStatus
    
    # Execution details
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Results
    output_data: Dict[str, Any] = Field(default_factory=dict)
    step_results: Dict[str, Any] = Field(default_factory=dict)
    
    # Error information
    error_message: Optional[str] = None
    error_step_id: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Metrics
    steps_completed: int = 0
    steps_total: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of completed steps."""
        if self.steps_total == 0:
            return 0.0
        return self.steps_completed / self.steps_total
    
    def mark_completed(self, success: bool = True) -> None:
        """Mark workflow as completed."""
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.status = WorkflowStatus.COMPLETED if success else WorkflowStatus.FAILED


class Workflow(BaseModel):
    """Complete workflow definition."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    version: str = Field(default="1.0.0")
    
    # Workflow configuration
    steps: List[WorkflowStep] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution settings
    max_execution_time_seconds: Optional[int] = Field(None, ge=1)
    parallel_execution: bool = Field(default=False)
    
    # Status and metadata
    status: WorkflowStatus = Field(default=WorkflowStatus.DRAFT)
    tags: List[str] = Field(default_factory=list)
    
    # Ownership and permissions
    created_by: Optional[str] = Field(None, description="User ID who created the workflow")
    shared_with: List[str] = Field(default_factory=list, description="User IDs with access")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_executed_at: Optional[datetime] = None
    
    # Execution history
    execution_count: int = Field(default=0, ge=0)
    success_count: int = Field(default=0, ge=0)
    
    @validator("steps")
    def validate_steps(cls, v: List[WorkflowStep]) -> List[WorkflowStep]:
        """Validate workflow steps."""
        if not v:
            return v
        
        # Check for duplicate step IDs
        step_ids = [step.id for step in v]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("Duplicate step IDs found")
        
        # Check for duplicate order values
        orders = [step.order for step in v]
        if len(orders) != len(set(orders)):
            raise ValueError("Duplicate step order values found")
        
        # Validate dependencies
        for step in v:
            for dep_id in step.depends_on:
                if dep_id not in step_ids:
                    raise ValueError(f"Step {step.id} depends on non-existent step {dep_id}")
                
                # Check for circular dependencies (basic check)
                dep_step = next(s for s in v if s.id == dep_id)
                if step.id in dep_step.depends_on:
                    raise ValueError(f"Circular dependency detected between {step.id} and {dep_id}")
        
        return v
    
    @property
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count
    
    @property
    def is_executable(self) -> bool:
        """Check if workflow can be executed."""
        return (
            self.status in [WorkflowStatus.READY, WorkflowStatus.COMPLETED, WorkflowStatus.FAILED] and
            len(self.steps) > 0
        )
    
    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow."""
        # Auto-assign order if not set
        if step.order == 0 and self.steps:
            step.order = max(s.order for s in self.steps) + 1
        
        self.steps.append(step)
        self.update_timestamp()
    
    def remove_step(self, step_id: str) -> bool:
        """Remove a step from the workflow."""
        original_count = len(self.steps)
        self.steps = [s for s in self.steps if s.id != step_id]
        
        if len(self.steps) < original_count:
            # Remove dependencies on the deleted step
            for step in self.steps:
                step.depends_on = [dep for dep in step.depends_on if dep != step_id]
            
            self.update_timestamp()
            return True
        
        return False
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID."""
        return next((s for s in self.steps if s.id == step_id), None)
    
    def get_steps_by_order(self) -> List[WorkflowStep]:
        """Get steps sorted by execution order."""
        return sorted(self.steps, key=lambda s: s.order)
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def mark_executed(self, success: bool = True) -> None:
        """Mark workflow as executed."""
        self.last_executed_at = datetime.utcnow()
        self.execution_count += 1
        if success:
            self.success_count += 1
        self.update_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        """Create workflow from dictionary."""
        return cls(**data)


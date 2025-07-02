"""
Task Pydantic Schemas
Task: 1.8 - Integrate ORM Models with FastAPI
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from enum import Enum

from .common import BaseSchema, TimestampMixin


class TaskStatus(str, Enum):
    """Status da tarefa"""
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class TaskPriority(str, Enum):
    """Prioridade da tarefa"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskBase(BaseModel):
    """Schema base da tarefa"""
    task_type_id: int
    provider_model_id: Optional[int] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    request_payload: Dict[str, Any]
    campaign_id: Optional[UUID4] = None


class TaskCreate(TaskBase):
    """Schema para criação de tarefa"""
    pass


class TaskUpdate(BaseModel):
    """Schema para atualização de tarefa"""
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class TaskResponse(BaseSchema):
    """Schema de resposta da tarefa"""
    id: UUID4
    user_id: int
    task_type_id: int
    provider_model_id: Optional[int]
    status: TaskStatus
    priority: TaskPriority
    credit_cost: int
    estimated_cost: Optional[int]
    request_payload: Dict[str, Any]
    result_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    retry_count: int
    execution_time_ms: Optional[int]
    campaign_id: Optional[UUID4]
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Campos calculados
    is_completed: bool = Field(description="Se a tarefa foi completada")
    is_running: bool = Field(description="Se a tarefa está em execução")
    
    class Config:
        orm_mode = True


class TaskSummary(BaseModel):
    """Schema resumido da tarefa"""
    id: UUID4
    status: TaskStatus
    priority: TaskPriority
    credit_cost: int
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        orm_mode = True 
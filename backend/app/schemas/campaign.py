"""
Campaign Pydantic Schemas
Task: 1.8 - Integrate ORM Models with FastAPI
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from enum import Enum

from .common import BaseSchema


class CampaignStatus(str, Enum):
    """Status da campanha"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class CampaignCreate(BaseModel):
    """Schema para criação de campanha"""
    name: str = Field(max_length=255)
    description: Optional[str] = None
    campaign_type_id: int
    channels: List[str]
    objectives: Dict[str, Any]
    budget_credits: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    """Schema para atualização de campanha"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    channels: Optional[List[str]] = None
    objectives: Optional[Dict[str, Any]] = None
    budget_credits: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CampaignResponse(BaseSchema):
    """Schema de resposta da campanha"""
    id: UUID4
    user_id: int
    name: str
    description: Optional[str]
    campaign_type_id: int
    status: CampaignStatus
    channels: List[str]
    objectives: Dict[str, Any]
    budget_credits: Optional[int]
    spent_credits: int
    metrics: Optional[Dict[str, Any]]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    launched_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime 
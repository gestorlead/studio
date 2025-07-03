"""
Agent schemas for request/response validation
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.schemas.common import TimestampMixin


class AgentBase(BaseModel):
    """Base agent schema"""
    name: str
    description: Optional[str] = None
    agent_type: str
    configuration: Optional[Dict[str, Any]] = None
    is_active: bool = True


class AgentCreate(AgentBase):
    """Schema for creating agent"""
    pass


class AgentUpdate(BaseModel):
    """Schema for updating agent"""
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AgentResponse(AgentBase, TimestampMixin):
    """Schema for agent response"""
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

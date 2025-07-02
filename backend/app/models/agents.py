"""
Agent model for GestorLead Studio
Based on Task 1.1 - Define Entity Models and Attributes
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModel

class Agent(Base, BaseModel):
    """Agent model for AI workflow automation"""
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("agent_categories.id"), nullable=True)
    type_id = Column(Integer, ForeignKey("agent_types.id"), nullable=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(50), nullable=False)  # workflow, scheduled, trigger_based, api_endpoint
    status = Column(String(20), nullable=False, default='draft')  # draft, active, inactive, archived, published
    is_public = Column(Boolean, nullable=False, default=False)
    category = Column(String(50), nullable=True)  # Legacy field
    tags = Column(JSON, nullable=True)
    
    configuration = Column(JSON, nullable=False)
    workflow_definition = Column(JSON, nullable=False)
    triggers = Column(JSON, nullable=True)
    variables = Column(JSON, nullable=True)
    permissions = Column(JSON, nullable=True)
    
    version = Column(String(20), nullable=False, default='1.0.0')
    execution_count = Column(Integer, nullable=False, default=0)
    success_rate = Column(Numeric(5, 4), nullable=True)  # 0.0000 - 1.0000
    avg_execution_time_ms = Column(Integer, nullable=True)
    last_executed_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="agents")
    category = relationship("AgentCategory", back_populates="agents")
    agent_type_rel = relationship("AgentType", back_populates="agents")
    
    def __repr__(self):
        return f"<Agent(id='{self.id}', name='{self.name}')>"

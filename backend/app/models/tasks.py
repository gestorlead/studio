"""
Task model for GestorLead Studio
Based on Task 1.1 - Define Entity Models and Attributes
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModel

class Task(Base, BaseModel):
    """Task model for AI processing tasks"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_type_id = Column(Integer, ForeignKey("task_types.id"), nullable=True)
    provider_model_id = Column(Integer, ForeignKey("provider_models.id"), nullable=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=True)
    
    # Legacy fields (for compatibility during migration)
    task_type = Column(String(50), nullable=True, index=True)
    provider = Column(String(50), nullable=True, index=True)
    model = Column(String(100), nullable=True)
    
    status = Column(String(20), nullable=False, default='pending', index=True)
    priority = Column(String(10), nullable=False, default='medium')
    credit_cost = Column(Integer, nullable=False)
    estimated_cost = Column(Integer, nullable=True)
    
    request_payload = Column(JSON, nullable=False)
    result_payload = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    execution_time_ms = Column(Integer, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    task_type_rel = relationship("TaskType", back_populates="tasks")
    provider_model = relationship("ProviderModel", back_populates="tasks")
    campaign = relationship("Campaign", back_populates="tasks")
    generated_content = relationship("GeneratedContent", back_populates="task", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id='{self.id}', status='{self.status}')>"

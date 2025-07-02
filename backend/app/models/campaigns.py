"""
Campaign model for GestorLead Studio
Based on Task 1.1 - Define Entity Models and Attributes
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModel

class Campaign(Base, BaseModel):
    """Campaign model for marketing campaigns"""
    __tablename__ = "campaigns"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    campaign_type_id = Column(Integer, ForeignKey("campaign_types.id"), nullable=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    campaign_type = Column(String(50), nullable=True)  # Legacy field
    status = Column(String(20), nullable=False, default='draft')  # draft, scheduled, active, paused, completed, cancelled, archived
    
    channels = Column(JSON, nullable=False)  # social media, email, etc.
    target_audience = Column(JSON, nullable=True)
    objectives = Column(JSON, nullable=False)
    budget_credits = Column(Integer, nullable=True)
    spent_credits = Column(Integer, nullable=False, default=0)
    
    content_templates = Column(JSON, nullable=True)
    scheduling = Column(JSON, nullable=True)
    automation_rules = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    a_b_testing = Column(JSON, nullable=True)
    
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    launched_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    campaign_type_rel = relationship("CampaignType", back_populates="campaigns")
    tasks = relationship("Task", back_populates="campaign")
    
    def __repr__(self):
        return f"<Campaign(id='{self.id}', name='{self.name}')>"

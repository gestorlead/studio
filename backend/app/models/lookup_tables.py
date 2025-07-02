"""
Lookup tables models for GestorLead Studio
Based on Task 1.3 - Normalize Database Schema
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class TaskType(Base):
    """Task types lookup table"""
    __tablename__ = "task_types"
    
    id = Column(Integer, primary_key=True)
    type_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))
    default_credit_cost = Column(Integer, default=1)
    
    # Relationships
    tasks = relationship("Task", back_populates="task_type")

class ProviderModel(Base):
    """Provider models lookup table"""
    __tablename__ = "provider_models"
    
    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)
    task_types = Column(JSON, nullable=False)  # Array of supported task types
    cost_per_credit = Column(Integer)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        {"schema": None},  # Ensure we're using the default schema
    )
    
    # Relationships
    tasks = relationship("Task", back_populates="provider_model")

class AgentCategory(Base):
    """Agent categories lookup table"""
    __tablename__ = "agent_categories"
    
    id = Column(Integer, primary_key=True)
    category_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    agent_types = relationship("AgentType", back_populates="category")
    agents = relationship("Agent", back_populates="category")

class AgentType(Base):
    """Agent types lookup table"""
    __tablename__ = "agent_types"
    
    id = Column(Integer, primary_key=True)
    type_name = Column(String(50), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("agent_categories.id"), nullable=False)
    description = Column(Text)
    default_config = Column(JSON)
    
    # Relationships
    category = relationship("AgentCategory", back_populates="agent_types")
    agents = relationship("Agent", back_populates="agent_type")

class CampaignType(Base):
    """Campaign types lookup table"""
    __tablename__ = "campaign_types"
    
    id = Column(Integer, primary_key=True)
    type_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    default_channels = Column(JSON)
    estimated_duration_days = Column(Integer)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="campaign_type")

class AIProvider(Base):
    """AI providers lookup table"""
    __tablename__ = "ai_providers"
    
    id = Column(Integer, primary_key=True)
    provider_name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100))
    api_base_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="provider")

class SubscriptionTier(Base):
    """Subscription tiers lookup table"""
    __tablename__ = "subscription_tiers"
    
    id = Column(Integer, primary_key=True)
    tier_name = Column(String(50), unique=True, nullable=False)
    monthly_credits = Column(Integer, nullable=False)
    max_agents = Column(Integer)
    monthly_price_cents = Column(Integer)
    
    # Relationships
    users = relationship("User", back_populates="subscription_tier")

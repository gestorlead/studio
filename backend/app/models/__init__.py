"""
GestorLead Studio - SQLAlchemy ORM Models
Task 1.7: Implement SQLAlchemy ORM Models

Este módulo contém todos os modelos SQLAlchemy ORM para o sistema GestorLead Studio.
"""

from .base import Base
from .user import User
from .task import Task
from .agent import Agent
from .campaign import Campaign
from .generated_content import GeneratedContent
from .api_key import APIKey

# Lookup tables
from .lookup import (
    SubscriptionTier,
    AIProvider,
    TaskType,
    ProviderModel,
    AgentCategory,
    AgentType,
    CampaignType
)

__all__ = [
    # Base
    "Base",
    
    # Core entities
    "User",
    "Task", 
    "Agent",
    "Campaign",
    "GeneratedContent",
    "APIKey",
    
    # Lookup tables
    "SubscriptionTier",
    "AIProvider",
    "TaskType",
    "ProviderModel",
    "AgentCategory", 
    "AgentType",
    "CampaignType"
]

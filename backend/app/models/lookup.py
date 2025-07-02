"""
GestorLead Studio - Lookup Tables ORM Models
Task 1.7: Implement SQLAlchemy ORM Models

Modelos para tabelas de lookup e referência do sistema.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Integer, String, Boolean, DateTime, Text, JSON, 
    ForeignKey, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class SubscriptionTier(Base, TimestampMixin):
    """
    Tabela de níveis de assinatura disponíveis no sistema.
    """
    __tablename__ = "subscription_tiers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tier_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    monthly_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    max_agents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    monthly_price_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="subscription_tier")
    
    __table_args__ = (
        CheckConstraint('monthly_credits >= 0', name='monthly_credits_non_negative'),
        CheckConstraint('max_agents IS NULL OR max_agents >= 0', name='max_agents_non_negative'),
        CheckConstraint('monthly_price_cents IS NULL OR monthly_price_cents >= 0', name='price_non_negative'),
    )


class AIProvider(Base, TimestampMixin):
    """
    Tabela de provedores de IA suportados pelo sistema.
    """
    __tablename__ = "ai_providers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    api_base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    api_keys: Mapped[List["APIKey"]] = relationship("APIKey", back_populates="provider_ref")


class TaskType(Base, TimestampMixin):
    """
    Tabela de tipos de tarefas de IA disponíveis.
    """
    __tablename__ = "task_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    default_credit_cost: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Relationships
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="task_type_ref")
    
    __table_args__ = (
        CheckConstraint('default_credit_cost >= 0', name='default_credit_cost_non_negative'),
    )


class ProviderModel(Base, TimestampMixin):
    """
    Tabela de modelos disponíveis por provedor de IA.
    """
    __tablename__ = "provider_models"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    task_types: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    cost_per_credit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="provider_model_ref")
    
    __table_args__ = (
        CheckConstraint('cost_per_credit IS NULL OR cost_per_credit >= 0', name='cost_per_credit_non_negative'),
        CheckConstraint("task_types != 'null'::json AND task_types != '[]'::json", name='task_types_not_empty'),
    )


class AgentCategory(Base, TimestampMixin):
    """
    Tabela de categorias de agentes para organização.
    """
    __tablename__ = "agent_categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    agent_types: Mapped[List["AgentType"]] = relationship("AgentType", back_populates="category")
    agents: Mapped[List["Agent"]] = relationship("Agent", back_populates="category_ref")
    
    __table_args__ = (
        CheckConstraint('sort_order >= 0', name='sort_order_non_negative'),
    )


class AgentType(Base, TimestampMixin):
    """
    Tabela de tipos de agentes disponíveis.
    """
    __tablename__ = "agent_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('agent_categories.id'), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    category: Mapped["AgentCategory"] = relationship("AgentCategory", back_populates="agent_types")
    agents: Mapped[List["Agent"]] = relationship("Agent", back_populates="type_ref")


class CampaignType(Base, TimestampMixin):
    """
    Tabela de tipos de campanhas disponíveis.
    """
    __tablename__ = "campaign_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_channels: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    estimated_duration_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Relationships
    campaigns: Mapped[List["Campaign"]] = relationship("Campaign", back_populates="campaign_type_ref")
    
    __table_args__ = (
        CheckConstraint('estimated_duration_days IS NULL OR estimated_duration_days > 0', name='duration_positive'),
    ) 
"""
GestorLead Studio - User ORM Model
Task 1.7: Implement SQLAlchemy ORM Models

Modelo principal de usuários do sistema com autenticação, perfil e créditos.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Integer, String, Boolean, DateTime, JSON,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base, TimestampMixin
from ..models.entity_types import SubscriptionTier, validate_email, validate_credit_balance


class User(Base, TimestampMixin):
    """
    Modelo de usuários do sistema GestorLead Studio.
    
    Representa usuários da plataforma, incluindo informações de autenticação,
    perfil, configurações e saldo de créditos.
    """
    __tablename__ = "users"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True,
        doc="Email do usuário (usado para login)"
    )
    google_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True, index=True,
        doc="ID do Google OAuth (para login social)"
    )
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
        doc="Hash da senha (nullable para usuários OAuth)"
    )
    
    # Profile fields
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
        doc="Nome completo do usuário"
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
        doc="URL do avatar/foto de perfil"
    )
    
    # Subscription and credits
    credit_balance: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
        doc="Saldo atual de créditos"
    )
    subscription_tier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('subscription_tiers.id'), nullable=True,
        doc="Referência ao nível de assinatura"
    )
    
    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        doc="Status ativo/inativo da conta"
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        doc="Flag de administrador"
    )
    
    # Configuration and metadata
    preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Configurações e preferências do usuário"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Último login do usuário"
    )
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de verificação do email"
    )
    
    # ===== RELATIONSHIPS =====
    
    # Subscription relationship
    subscription_tier: Mapped[Optional["SubscriptionTier"]] = relationship(
        "SubscriptionTier", back_populates="users"
    )
    
    # Tasks relationship (1:N)
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="user", cascade="all, delete-orphan"
    )
    
    # Agents relationship (1:N)
    agents: Mapped[List["Agent"]] = relationship(
        "Agent", back_populates="user", cascade="all, delete-orphan"
    )
    
    # Campaigns relationship (1:N)
    campaigns: Mapped[List["Campaign"]] = relationship(
        "Campaign", back_populates="user", cascade="all, delete-orphan"
    )
    
    # API Keys relationship (1:N)
    api_keys: Mapped[List["APIKey"]] = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan"
    )
    
    # Generated Content relationship (1:N)
    generated_content: Mapped[List["GeneratedContent"]] = relationship(
        "GeneratedContent", back_populates="user", cascade="all, delete-orphan"
    )
    
    # ===== CONSTRAINTS AND INDEXES =====
    
    __table_args__ = (
        # Check constraints
        CheckConstraint('credit_balance >= 0', name='credit_balance_non_negative'),
        CheckConstraint(
            'last_login_at IS NULL OR last_login_at <= updated_at', 
            name='last_login_before_update'
        ),
        CheckConstraint(
            'email_verified_at IS NULL OR email_verified_at <= updated_at', 
            name='email_verified_before_update'
        ),
        
        # Performance indexes
        Index('idx_users_email', 'email'),
        Index('idx_users_google_id', 'google_id'),
        Index('idx_users_subscription_tier', 'subscription_tier_id'),
        Index('idx_users_status', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
    )
    
    # ===== HYBRID PROPERTIES =====
    
    @hybrid_property
    def is_verified(self) -> bool:
        """Verifica se o email do usuário foi verificado."""
        return self.email_verified_at is not None
    
    @hybrid_property
    def has_credits(self) -> bool:
        """Verifica se o usuário possui créditos disponíveis."""
        return self.credit_balance > 0
    
    @hybrid_property
    def subscription_tier_name(self) -> Optional[str]:
        """Retorna o nome do nível de assinatura atual."""
        if self.subscription_tier:
            return self.subscription_tier.tier_name
        return "free"
    
    # ===== METHODS =====
    
    def can_spend_credits(self, amount: int) -> bool:
        """
        Verifica se o usuário pode gastar uma quantidade específica de créditos.
        
        Args:
            amount: Quantidade de créditos a ser gasta
            
        Returns:
            True se o usuário tem créditos suficientes
        """
        return self.credit_balance >= amount
    
    def spend_credits(self, amount: int) -> bool:
        """
        Gasta créditos do usuário.
        
        Args:
            amount: Quantidade de créditos a ser gasta
            
        Returns:
            True se os créditos foram gastos com sucesso
            
        Raises:
            ValueError: Se não há créditos suficientes
        """
        if not self.can_spend_credits(amount):
            raise ValueError(f"Insufficient credits. Balance: {self.credit_balance}, Required: {amount}")
        
        self.credit_balance -= amount
        return True
    
    def add_credits(self, amount: int) -> None:
        """
        Adiciona créditos ao usuário.
        
        Args:
            amount: Quantidade de créditos a ser adicionada
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        self.credit_balance += amount
    
    def verify_email(self) -> None:
        """Marca o email como verificado."""
        self.email_verified_at = datetime.utcnow()
    
    def update_last_login(self) -> None:
        """Atualiza o timestamp do último login."""
        self.last_login_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Desativa a conta do usuário."""
        self.is_active = False
    
    def activate(self) -> None:
        """Ativa a conta do usuário."""
        self.is_active = True
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Converte o usuário para dicionário.
        
        Args:
            include_sensitive: Se True, inclui informações sensíveis
            
        Returns:
            Dicionário com os dados do usuário
        """
        exclude = {'password_hash'} if not include_sensitive else set()
        data = super().to_dict(exclude=exclude)
        
        # Adicionar propriedades computadas
        data.update({
            'is_verified': self.is_verified,
            'has_credits': self.has_credits,
            'subscription_tier_name': self.subscription_tier_name
        })
        
        return data
    
    def __repr__(self) -> str:
        """Representação string do usuário."""
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>" 
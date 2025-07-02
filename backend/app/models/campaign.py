"""
GestorLead Studio - Campaign ORM Model
Task 1.7: Implement SQLAlchemy ORM Models

Modelo de campanhas de marketing que podem incluir múltiplas tarefas e execuções de agentes.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, JSON,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base, TimestampMixin


class Campaign(Base, TimestampMixin):
    """
    Modelo de campanhas de marketing do sistema GestorLead Studio.
    
    Representa campanhas de marketing que podem incluir múltiplas tarefas
    e execuções de agentes.
    """
    __tablename__ = "campaigns"
    
    # Primary Key (UUID)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False, index=True,
        doc="Proprietário da campanha"
    )
    campaign_type_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('campaign_types.id'), nullable=True,
        doc="Referência ao tipo de campanha"
    )
    
    # Basic information
    name: Mapped[str] = mapped_column(
        String(255), nullable=False,
        doc="Nome da campanha"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        doc="Descrição detalhada"
    )
    
    # Campaign configuration
    campaign_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
        doc="Tipo de campanha"
    )
    status: Mapped[str] = mapped_column(
        String(20), default='draft', nullable=False,
        doc="Status atual"
    )
    
    # Target and strategy
    channels: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False,
        doc="Canais utilizados (social media, email, etc.)"
    )
    target_audience: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Definição do público-alvo"
    )
    objectives: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False,
        doc="Objetivos e KPIs da campanha"
    )
    
    # Budget and costs
    budget_credits: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        doc="Orçamento em créditos"
    )
    spent_credits: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
        doc="Créditos já utilizados"
    )
    
    # Content and automation
    content_templates: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Templates de conteúdo"
    )
    scheduling: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Configurações de agendamento"
    )
    automation_rules: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Regras de automação"
    )
    
    # Analytics and testing
    metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Métricas e resultados"
    )
    a_b_testing: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Configurações de teste A/B"
    )
    
    # Timeline
    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de início planejada"
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de fim planejada"
    )
    launched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de lançamento efetiva"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de conclusão"
    )
    
    # ===== RELATIONSHIPS =====
    
    # User relationship (N:1)
    user: Mapped["User"] = relationship("User", back_populates="campaigns")
    
    # Campaign type relationship (N:1)
    campaign_type_ref: Mapped[Optional["CampaignType"]] = relationship(
        "CampaignType", back_populates="campaigns"
    )
    
    # Tasks relationship (1:N)
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="campaign", cascade="all, delete-orphan"
    )
    
    # ===== CONSTRAINTS AND INDEXES =====
    
    __table_args__ = (
        # Check constraints
        CheckConstraint(
            "status IN ('draft', 'scheduled', 'active', 'paused', 'completed', 'cancelled', 'archived')",
            name='valid_campaign_status'
        ),
        CheckConstraint('budget_credits IS NULL OR budget_credits > 0', name='budget_positive'),
        CheckConstraint('spent_credits >= 0', name='spent_credits_non_negative'),
        CheckConstraint(
            'spent_credits <= COALESCE(budget_credits, spent_credits)',
            name='spent_within_budget'
        ),
        CheckConstraint(
            'start_date IS NULL OR end_date IS NULL OR start_date <= end_date',
            name='start_before_end'
        ),
        CheckConstraint(
            "channels != 'null'::json AND channels != '[]'::json",
            name='channels_not_empty'
        ),
        CheckConstraint(
            "objectives != 'null'::json AND objectives != '{}'::json",
            name='objectives_not_empty'
        ),
        
        # Performance indexes
        Index('idx_campaigns_user_id', 'user_id'),
        Index('idx_campaigns_status', 'status'),
        Index('idx_campaigns_created_at', 'created_at'),
        Index('idx_campaigns_user_status', 'user_id', 'status'),
        Index('idx_campaigns_dates', 'start_date', 'end_date'),
    )
    
    # ===== HYBRID PROPERTIES =====
    
    @hybrid_property
    def is_active(self) -> bool:
        """Verifica se a campanha está ativa."""
        return self.status == 'active'
    
    @hybrid_property
    def is_completed(self) -> bool:
        """Verifica se a campanha foi concluída."""
        return self.status == 'completed'
    
    @hybrid_property
    def is_draft(self) -> bool:
        """Verifica se a campanha está em rascunho."""
        return self.status == 'draft'
    
    @hybrid_property
    def is_launched(self) -> bool:
        """Verifica se a campanha foi lançada."""
        return self.launched_at is not None
    
    @hybrid_property
    def has_budget(self) -> bool:
        """Verifica se a campanha tem orçamento definido."""
        return self.budget_credits is not None and self.budget_credits > 0
    
    @hybrid_property
    def remaining_credits(self) -> Optional[int]:
        """Retorna os créditos restantes no orçamento."""
        if self.budget_credits is None:
            return None
        return self.budget_credits - self.spent_credits
    
    @hybrid_property
    def budget_utilization(self) -> Optional[float]:
        """Retorna a porcentagem de utilização do orçamento."""
        if self.budget_credits is None or self.budget_credits == 0:
            return None
        return (self.spent_credits / self.budget_credits) * 100
    
    @hybrid_property
    def duration_days(self) -> Optional[int]:
        """Retorna a duração planejada da campanha em dias."""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return delta.days
        return None
    
    # ===== METHODS =====
    
    def launch(self) -> None:
        """Lança a campanha."""
        if self.status == 'draft':
            self.status = 'active'
            self.launched_at = datetime.utcnow()
    
    def pause(self) -> None:
        """Pausa a campanha."""
        if self.status == 'active':
            self.status = 'paused'
    
    def resume(self) -> None:
        """Resume a campanha pausada."""
        if self.status == 'paused':
            self.status = 'active'
    
    def complete(self) -> None:
        """Marca a campanha como concluída."""
        if self.status in ('active', 'paused'):
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancela a campanha."""
        if self.status in ('draft', 'scheduled', 'active', 'paused'):
            self.status = 'cancelled'
            if not self.completed_at:
                self.completed_at = datetime.utcnow()
    
    def archive(self) -> None:
        """Arquiva a campanha."""
        if self.status in ('completed', 'cancelled'):
            self.status = 'archived'
    
    def can_spend_credits(self, amount: int) -> bool:
        """
        Verifica se a campanha pode gastar créditos.
        
        Args:
            amount: Quantidade de créditos a ser gasta
            
        Returns:
            True se há orçamento suficiente
        """
        if self.budget_credits is None:
            return True  # Sem limite de orçamento
        return self.spent_credits + amount <= self.budget_credits
    
    def spend_credits(self, amount: int) -> bool:
        """
        Gasta créditos da campanha.
        
        Args:
            amount: Quantidade de créditos a ser gasta
            
        Returns:
            True se os créditos foram gastos com sucesso
            
        Raises:
            ValueError: Se não há orçamento suficiente
        """
        if not self.can_spend_credits(amount):
            raise ValueError(f"Insufficient budget. Available: {self.remaining_credits}, Required: {amount}")
        
        self.spent_credits += amount
        return True
    
    def get_channel_list(self) -> List[str]:
        """Retorna a lista de canais da campanha."""
        if isinstance(self.channels, dict):
            return list(self.channels.keys())
        elif isinstance(self.channels, list):
            return self.channels
        return []
    
    def get_objective_list(self) -> List[str]:
        """Retorna a lista de objetivos da campanha."""
        if isinstance(self.objectives, dict):
            if 'objectives' in self.objectives:
                return self.objectives['objectives']
            return list(self.objectives.keys())
        elif isinstance(self.objectives, list):
            return self.objectives
        return []
    
    def add_metric(self, metric_name: str, value: Any, timestamp: Optional[datetime] = None) -> None:
        """
        Adiciona uma métrica à campanha.
        
        Args:
            metric_name: Nome da métrica
            value: Valor da métrica
            timestamp: Timestamp da métrica (default: agora)
        """
        if self.metrics is None:
            self.metrics = {}
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': timestamp.isoformat()
        })
    
    def get_campaign_type_name(self) -> Optional[str]:
        """Retorna o nome do tipo de campanha."""
        if self.campaign_type_ref:
            return self.campaign_type_ref.type_name
        return self.campaign_type
    
    def to_dict(self, include_details: bool = True) -> Dict[str, Any]:
        """
        Converte a campanha para dicionário.
        
        Args:
            include_details: Se True, inclui configurações detalhadas
            
        Returns:
            Dicionário com os dados da campanha
        """
        exclude = set()
        if not include_details:
            exclude.update({
                'content_templates', 'automation_rules', 'scheduling',
                'metrics', 'a_b_testing'
            })
        
        data = super().to_dict(exclude=exclude)
        
        # Adicionar propriedades computadas
        data.update({
            'is_active': self.is_active,
            'is_completed': self.is_completed,
            'is_draft': self.is_draft,
            'is_launched': self.is_launched,
            'has_budget': self.has_budget,
            'remaining_credits': self.remaining_credits,
            'budget_utilization': self.budget_utilization,
            'duration_days': self.duration_days,
            'channel_list': self.get_channel_list(),
            'objective_list': self.get_objective_list(),
            'campaign_type_name': self.get_campaign_type_name()
        })
        
        return data
    
    def __repr__(self) -> str:
        """Representação string da campanha."""
        return f"<Campaign(id={self.id}, name='{self.name}', status='{self.status}')>"

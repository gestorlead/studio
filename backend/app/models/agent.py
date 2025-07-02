"""
GestorLead Studio - Agent ORM Model
Task 1.7: Implement SQLAlchemy ORM Models

Modelo de agentes IA customizados criados pelos usuários.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, JSON, Numeric,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base, TimestampMixin
from ..models.entity_types import AgentType as AgentTypeEnum, AgentStatus, AgentCategory as AgentCategoryEnum


class Agent(Base, TimestampMixin):
    """
    Modelo de agentes IA do sistema GestorLead Studio.
    
    Representa agentes IA customizados criados pelos usuários para automação
    de workflows complexos.
    """
    __tablename__ = "agents"
    
    # Primary Key (UUID)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False, index=True,
        doc="Proprietário do agente"
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('agent_categories.id'), nullable=True,
        doc="Categoria do agente"
    )
    type_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('agent_types.id'), nullable=True,
        doc="Tipo do agente"
    )
    
    # Basic information
    name: Mapped[str] = mapped_column(
        String(255), nullable=False,
        doc="Nome do agente"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        doc="Descrição detalhada do agente"
    )
    
    # Agent configuration
    agent_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        doc="Tipo do agente (workflow, scheduled, trigger_based)"
    )
    status: Mapped[str] = mapped_column(
        String(20), default='draft', nullable=False,
        doc="Status do agente"
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        doc="Se o agente é público no marketplace"
    )
    
    # Organization
    category: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
        doc="Categoria do agente (marketing, content, analytics)"
    )
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Tags para organização e busca"
    )
    
    # Core configuration
    configuration: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False,
        doc="Configuração completa do agente"
    )
    workflow_definition: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False,
        doc="Definição do workflow (nós, conexões, etc.)"
    )
    triggers: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Definição de triggers automáticos"
    )
    variables: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Variáveis configuráveis do agente"
    )
    permissions: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Permissões e limitações"
    )
    
    # Version and metrics
    version: Mapped[str] = mapped_column(
        String(20), default='1.0.0', nullable=False,
        doc="Versão do agente"
    )
    execution_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
        doc="Número total de execuções"
    )
    success_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True,
        doc="Taxa de sucesso (0.0000 - 1.0000)"
    )
    avg_execution_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        doc="Tempo médio de execução"
    )
    
    # Timestamps
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Última execução"
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de publicação no marketplace"
    )
    
    # ===== RELATIONSHIPS =====
    
    # User relationship (N:1)
    user: Mapped["User"] = relationship("User", back_populates="agents")
    
    # Category relationship (N:1)
    category_ref: Mapped[Optional["AgentCategory"]] = relationship(
        "AgentCategory", back_populates="agents"
    )
    
    # Type relationship (N:1)
    type_ref: Mapped[Optional["AgentType"]] = relationship(
        "AgentType", back_populates="agents"
    )
    
    # ===== CONSTRAINTS AND INDEXES =====
    
    __table_args__ = (
        # Check constraints
        CheckConstraint(
            "agent_type IN ('workflow', 'scheduled', 'trigger_based', 'api_endpoint')",
            name='valid_agent_type'
        ),
        CheckConstraint(
            "status IN ('draft', 'active', 'inactive', 'archived', 'published')",
            name='valid_agent_status'
        ),
        CheckConstraint('execution_count >= 0', name='execution_count_non_negative'),
        CheckConstraint(
            'success_rate IS NULL OR (success_rate >= 0 AND success_rate <= 1)',
            name='success_rate_valid'
        ),
        CheckConstraint(
            'avg_execution_time_ms IS NULL OR avg_execution_time_ms >= 0',
            name='avg_time_non_negative'
        ),
        CheckConstraint(
            "configuration != 'null'::json AND configuration != '{}'::json",
            name='configuration_not_empty'
        ),
        CheckConstraint(
            "workflow_definition != 'null'::json AND workflow_definition != '{}'::json",
            name='workflow_not_empty'
        ),
        
        # Performance indexes
        Index('idx_agents_user_id', 'user_id'),
        Index('idx_agents_status', 'status'),
        Index('idx_agents_type', 'agent_type'),
        Index('idx_agents_public', 'is_public'),
        Index('idx_agents_category', 'category_id'),
        Index('idx_agents_user_status', 'user_id', 'status'),
    )
    
    # ===== HYBRID PROPERTIES =====
    
    @hybrid_property
    def is_active(self) -> bool:
        """Verifica se o agente está ativo."""
        return self.status == 'active'
    
    @hybrid_property
    def is_published(self) -> bool:
        """Verifica se o agente foi publicado."""
        return self.status == 'published' and self.published_at is not None
    
    @hybrid_property
    def is_draft(self) -> bool:
        """Verifica se o agente está em rascunho."""
        return self.status == 'draft'
    
    @hybrid_property
    def has_executions(self) -> bool:
        """Verifica se o agente já foi executado."""
        return self.execution_count > 0
    
    @hybrid_property
    def success_percentage(self) -> Optional[float]:
        """Retorna a taxa de sucesso como porcentagem."""
        if self.success_rate is not None:
            return float(self.success_rate) * 100
        return None
    
    # ===== METHODS =====
    
    def activate(self) -> None:
        """Ativa o agente."""
        if self.status == 'draft':
            self.status = 'active'
    
    def deactivate(self) -> None:
        """Desativa o agente."""
        if self.status == 'active':
            self.status = 'inactive'
    
    def publish(self) -> None:
        """Publica o agente no marketplace."""
        if self.status in ('active', 'inactive'):
            self.status = 'published'
            self.published_at = datetime.utcnow()
            self.is_public = True
    
    def archive(self) -> None:
        """Arquiva o agente."""
        self.status = 'archived'
    
    def update_execution_stats(self, execution_time_ms: int, success: bool) -> None:
        """
        Atualiza as estatísticas de execução do agente.
        
        Args:
            execution_time_ms: Tempo de execução em milissegundos
            success: Se a execução foi bem-sucedida
        """
        # Incrementar contador de execuções
        self.execution_count += 1
        self.last_executed_at = datetime.utcnow()
        
        # Atualizar tempo médio de execução
        if self.avg_execution_time_ms is None:
            self.avg_execution_time_ms = execution_time_ms
        else:
            # Média ponderada
            total_time = self.avg_execution_time_ms * (self.execution_count - 1) + execution_time_ms
            self.avg_execution_time_ms = int(total_time / self.execution_count)
        
        # Atualizar taxa de sucesso
        if self.success_rate is None:
            self.success_rate = Decimal('1.0000' if success else '0.0000')
        else:
            # Calcular nova taxa de sucesso
            successes = int(float(self.success_rate) * (self.execution_count - 1))
            if success:
                successes += 1
            self.success_rate = Decimal(str(successes / self.execution_count)).quantize(Decimal('0.0001'))
    
    def increment_version(self, version_type: str = 'patch') -> str:
        """
        Incrementa a versão do agente.
        
        Args:
            version_type: Tipo de incremento ('major', 'minor', 'patch')
            
        Returns:
            Nova versão
        """
        try:
            parts = self.version.split('.')
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            
            if version_type == 'major':
                major += 1
                minor = 0
                patch = 0
            elif version_type == 'minor':
                minor += 1
                patch = 0
            else:  # patch
                patch += 1
            
            self.version = f"{major}.{minor}.{patch}"
            return self.version
        except (ValueError, IndexError):
            # Se a versão atual é inválida, resetar para 1.0.0
            self.version = "1.0.0"
            return self.version
    
    def get_category_name(self) -> Optional[str]:
        """Retorna o nome da categoria do agente."""
        if self.category_ref:
            return self.category_ref.category_name
        return self.category
    
    def get_type_name(self) -> Optional[str]:
        """Retorna o nome do tipo do agente."""
        if self.type_ref:
            return self.type_ref.type_name
        return self.agent_type
    
    def to_dict(self, include_definitions: bool = True) -> Dict[str, Any]:
        """
        Converte o agente para dicionário.
        
        Args:
            include_definitions: Se True, inclui workflow_definition e configuration
            
        Returns:
            Dicionário com os dados do agente
        """
        exclude = set()
        if not include_definitions:
            exclude.update({'workflow_definition', 'configuration', 'triggers', 'variables'})
        
        data = super().to_dict(exclude=exclude)
        
        # Adicionar propriedades computadas
        data.update({
            'is_active': self.is_active,
            'is_published': self.is_published,
            'is_draft': self.is_draft,
            'has_executions': self.has_executions,
            'success_percentage': self.success_percentage,
            'category_name': self.get_category_name(),
            'type_name': self.get_type_name()
        })
        
        return data
    
    def __repr__(self) -> str:
        """Representação string do agente."""
        return f"<Agent(id={self.id}, name='{self.name}', status='{self.status}')>" 
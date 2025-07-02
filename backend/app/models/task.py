"""
GestorLead Studio - Task ORM Model
Task 1.7: Implement SQLAlchemy ORM Models

Modelo de tarefas de IA executadas pelos usuários.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, JSON,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base, TimestampMixin
from ..models.entity_types import TaskStatus, TaskPriority, TaskType as TaskTypeEnum, AIProvider


class Task(Base, TimestampMixin):
    """
    Modelo de tarefas de IA do sistema GestorLead Studio.
    
    Representa tarefas de IA executadas pelos usuários, incluindo requests,
    responses e metadados de execução.
    """
    __tablename__ = "tasks"
    
    # Primary Key (UUID)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False, index=True,
        doc="Referência ao usuário proprietário"
    )
    task_type_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('task_types.id'), nullable=True,
        doc="Referência ao tipo de tarefa"
    )
    provider_model_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('provider_models.id'), nullable=True,
        doc="Referência ao modelo do provedor"
    )
    campaign_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey('campaigns.id'), nullable=True,
        doc="Referência à campanha (opcional)"
    )
    
    # Task identification
    task_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True,
        doc="Tipo da tarefa (text_generation, image_generation, etc.)"
    )
    provider: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True,
        doc="Provedor de IA (openai, google, piapi, elevenlabs)"
    )
    model: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        doc="Modelo específico usado (gpt-4, dall-e-3, etc.)"
    )
    
    # Execution status and priority
    status: Mapped[str] = mapped_column(
        String(20), default='pending', nullable=False, index=True,
        doc="Status da execução"
    )
    priority: Mapped[str] = mapped_column(
        String(10), default='medium', nullable=False,
        doc="Prioridade da tarefa (low, medium, high, urgent)"
    )
    
    # Cost information
    credit_cost: Mapped[int] = mapped_column(
        Integer, nullable=False,
        doc="Custo em créditos da tarefa"
    )
    estimated_cost: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        doc="Custo estimado antes da execução"
    )
    
    # Request and response data
    request_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False,
        doc="Dados da requisição (prompt, parâmetros, etc.)"
    )
    result_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Resultado da execução"
    )
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        doc="Mensagem de erro (se houver)"
    )
    error_code: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
        doc="Código de erro padronizado"
    )
    
    # Performance metrics
    execution_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        doc="Tempo de execução em milissegundos"
    )
    retry_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
        doc="Número de tentativas de execução"
    )
    
    # Scheduling timestamps
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data agendada para execução"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de início da execução"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de conclusão"
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de expiração do resultado"
    )
    
    # ===== RELATIONSHIPS =====
    
    # User relationship (N:1)
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    
    # Task type relationship (N:1)
    task_type_ref: Mapped[Optional["TaskType"]] = relationship(
        "TaskType", back_populates="tasks"
    )
    
    # Provider model relationship (N:1)
    provider_model_ref: Mapped[Optional["ProviderModel"]] = relationship(
        "ProviderModel", back_populates="tasks"
    )
    
    # Campaign relationship (N:1 optional)
    campaign: Mapped[Optional["Campaign"]] = relationship(
        "Campaign", back_populates="tasks"
    )
    
    # Generated content relationship (1:1)
    generated_content: Mapped[Optional["GeneratedContent"]] = relationship(
        "GeneratedContent", back_populates="task", uselist=False,
        cascade="all, delete-orphan"
    )
    
    # ===== CONSTRAINTS AND INDEXES =====
    
    __table_args__ = (
        # Check constraints
        CheckConstraint(
            "status IN ('pending', 'queued', 'processing', 'completed', 'failed', 'cancelled', 'retrying')",
            name='valid_task_status'
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'urgent')",
            name='valid_task_priority'
        ),
        CheckConstraint('credit_cost >= 0', name='credit_cost_non_negative'),
        CheckConstraint('estimated_cost IS NULL OR estimated_cost >= 0', name='estimated_cost_non_negative'),
        CheckConstraint('execution_time_ms IS NULL OR execution_time_ms >= 0', name='execution_time_non_negative'),
        CheckConstraint('retry_count >= 0', name='retry_count_non_negative'),
        CheckConstraint('started_at IS NULL OR started_at >= scheduled_at', name='started_after_scheduled'),
        CheckConstraint('completed_at IS NULL OR completed_at >= started_at', name='completed_after_started'),
        CheckConstraint(
            "request_payload != 'null'::json AND request_payload != '{}'::json",
            name='request_payload_not_empty'
        ),
        
        # Performance indexes
        Index('idx_tasks_user_id', 'user_id'),
        Index('idx_tasks_status', 'status'),
        Index('idx_tasks_created_at', 'created_at'),
        Index('idx_tasks_priority', 'priority'),
        Index('idx_tasks_user_status', 'user_id', 'status'),
        Index('idx_tasks_campaign_id', 'campaign_id'),
        Index('idx_tasks_provider_type', 'provider', 'task_type'),
    )
    
    # ===== HYBRID PROPERTIES =====
    
    @hybrid_property
    def is_completed(self) -> bool:
        """Verifica se a tarefa foi concluída."""
        return self.status == 'completed'
    
    @hybrid_property
    def is_failed(self) -> bool:
        """Verifica se a tarefa falhou."""
        return self.status == 'failed'
    
    @hybrid_property
    def is_running(self) -> bool:
        """Verifica se a tarefa está em execução."""
        return self.status in ('queued', 'processing')
    
    @hybrid_property
    def has_result(self) -> bool:
        """Verifica se a tarefa tem resultado disponível."""
        return self.result_payload is not None and self.is_completed
    
    @hybrid_property
    def execution_duration(self) -> Optional[int]:
        """Retorna a duração da execução em milissegundos."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() * 1000)
        return self.execution_time_ms
    
    # ===== METHODS =====
    
    def start_execution(self) -> None:
        """Marca o início da execução da tarefa."""
        self.status = 'processing'
        self.started_at = datetime.utcnow()
    
    def complete_execution(self, result: Dict[str, Any]) -> None:
        """
        Marca a tarefa como concluída com sucesso.
        
        Args:
            result: Resultado da execução
        """
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        self.result_payload = result
        
        # Calcular tempo de execução se possível
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.execution_time_ms = int(delta.total_seconds() * 1000)
    
    def fail_execution(self, error_message: str, error_code: Optional[str] = None) -> None:
        """
        Marca a tarefa como falhada.
        
        Args:
            error_message: Mensagem de erro
            error_code: Código de erro opcional
        """
        self.status = 'failed'
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        self.error_code = error_code
    
    def retry_execution(self) -> None:
        """Incrementa o contador de tentativas e reseta para execução."""
        self.retry_count += 1
        self.status = 'pending'
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.error_code = None
    
    def cancel_execution(self) -> None:
        """Cancela a execução da tarefa."""
        self.status = 'cancelled'
        if not self.completed_at:
            self.completed_at = datetime.utcnow()
    
    def get_prompt(self) -> Optional[str]:
        """Extrai o prompt principal da requisição."""
        if self.request_payload:
            return self.request_payload.get('prompt') or self.request_payload.get('text')
        return None
    
    def to_dict(self, include_payloads: bool = True) -> Dict[str, Any]:
        """
        Converte a tarefa para dicionário.
        
        Args:
            include_payloads: Se True, inclui request_payload e result_payload
            
        Returns:
            Dicionário com os dados da tarefa
        """
        exclude = set()
        if not include_payloads:
            exclude.update({'request_payload', 'result_payload'})
        
        data = super().to_dict(exclude=exclude)
        
        # Adicionar propriedades computadas
        data.update({
            'is_completed': self.is_completed,
            'is_failed': self.is_failed,
            'is_running': self.is_running,
            'has_result': self.has_result,
            'execution_duration': self.execution_duration,
            'prompt': self.get_prompt()
        })
        
        return data
    
    def __repr__(self) -> str:
        """Representação string da tarefa."""
        return f"<Task(id={self.id}, user_id={self.user_id}, status='{self.status}')>" 
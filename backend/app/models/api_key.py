"""
GestorLead Studio - APIKey ORM Model
Task 1.7: Implement SQLAlchemy ORM Models

Modelo de chaves de API dos usuários para diferentes provedores de IA.
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
from ..models.entity_types import AIProvider, ValidationStatus


class APIKey(Base, TimestampMixin):
    """
    Modelo de chaves de API do sistema GestorLead Studio.
    
    Armazena chaves de API dos usuários para diferentes provedores de IA,
    de forma segura e criptografada.
    """
    __tablename__ = "api_keys"
    
    # Primary Key (UUID)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False, index=True,
        doc="Proprietário da chave"
    )
    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('ai_providers.id'), nullable=True,
        doc="Referência ao provedor de IA"
    )
    
    # Provider identification
    provider: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True,
        doc="Provedor da API"
    )
    
    # Key information
    key_name: Mapped[str] = mapped_column(
        String(100), nullable=False,
        doc="Nome/identificação da chave"
    )
    encrypted_key: Mapped[str] = mapped_column(
        Text, nullable=False,
        doc="Chave criptografada"
    )
    key_hash: Mapped[str] = mapped_column(
        String(64), nullable=False,
        doc="Hash da chave para verificação"
    )
    
    # Configuration and limits
    permissions: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Permissões e limitações da chave"
    )
    usage_limits: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Limites de uso configurados"
    )
    usage_stats: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Estatísticas de uso"
    )
    
    # Status and configuration
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        doc="Status ativo/inativo"
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        doc="Chave padrão para o provedor"
    )
    
    # Expiration and validation
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de expiração da chave"
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Último uso da chave"
    )
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Última validação da chave"
    )
    validation_status: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True,
        doc="Status da última validação"
    )
    
    # Error tracking
    error_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
        doc="Contador de erros"
    )
    
    # ===== RELATIONSHIPS =====
    
    # User relationship (N:1)
    user: Mapped["User"] = relationship("User", back_populates="api_keys")
    
    # Provider relationship (N:1)
    provider_ref: Mapped[Optional["AIProvider"]] = relationship(
        "AIProvider", back_populates="api_keys"
    )
    
    # ===== CONSTRAINTS AND INDEXES =====
    
    __table_args__ = (
        # Check constraints
        CheckConstraint(
            "validation_status IN ('valid', 'invalid', 'expired', 'rate_limited', 'unknown') OR validation_status IS NULL",
            name='valid_validation_status'
        ),
        CheckConstraint('error_count >= 0', name='error_count_non_negative'),
        CheckConstraint('expires_at IS NULL OR expires_at > created_at', name='expires_after_created'),
        CheckConstraint('last_used_at IS NULL OR last_used_at <= updated_at', name='last_used_before_update'),
        
        # Performance indexes
        Index('idx_api_keys_user_id', 'user_id'),
        Index('idx_api_keys_provider', 'provider'),
        Index('idx_api_keys_hash', 'key_hash'),
        Index('idx_api_keys_user_provider', 'user_id', 'provider'),
        Index('idx_api_keys_active', 'is_active'),
        Index('idx_api_keys_default', 'is_default'),
    )
    
    # ===== HYBRID PROPERTIES =====
    
    @hybrid_property
    def is_valid(self) -> bool:
        """Verifica se a chave está válida."""
        return (
            self.is_active and 
            self.validation_status == 'valid' and
            (self.expires_at is None or self.expires_at > datetime.utcnow())
        )
    
    @hybrid_property
    def is_expired(self) -> bool:
        """Verifica se a chave expirou."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @hybrid_property
    def has_errors(self) -> bool:
        """Verifica se a chave tem erros registrados."""
        return self.error_count > 0
    
    @hybrid_property
    def needs_validation(self) -> bool:
        """Verifica se a chave precisa de validação."""
        if self.last_validated_at is None:
            return True
        
        # Se não foi validada nas últimas 24 horas
        from datetime import timedelta
        threshold = datetime.utcnow() - timedelta(hours=24)
        return self.last_validated_at < threshold
    
    @hybrid_property
    def usage_count(self) -> int:
        """Retorna o contador de uso da chave."""
        if self.usage_stats and isinstance(self.usage_stats, dict):
            return self.usage_stats.get('usage_count', 0)
        return 0
    
    # ===== METHODS =====
    
    def activate(self) -> None:
        """Ativa a chave de API."""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Desativa a chave de API."""
        self.is_active = False
    
    def set_as_default(self) -> None:
        """Define esta chave como padrão para o provedor."""
        self.is_default = True
    
    def unset_as_default(self) -> None:
        """Remove a marcação de padrão desta chave."""
        self.is_default = False
    
    def mark_as_used(self) -> None:
        """Marca a chave como usada e atualiza estatísticas."""
        self.last_used_at = datetime.utcnow()
        
        # Atualizar estatísticas de uso
        if self.usage_stats is None:
            self.usage_stats = {}
        
        current_count = self.usage_stats.get('usage_count', 0)
        self.usage_stats['usage_count'] = current_count + 1
        self.usage_stats['last_used'] = datetime.utcnow().isoformat()
    
    def increment_error_count(self) -> None:
        """Incrementa o contador de erros."""
        self.error_count += 1
        
        # Se muitos erros, desativar automaticamente
        if self.error_count >= 10:
            self.deactivate()
            self.validation_status = 'invalid'
    
    def reset_error_count(self) -> None:
        """Reseta o contador de erros."""
        self.error_count = 0
    
    def update_validation_status(self, status: str, error_message: Optional[str] = None) -> None:
        """
        Atualiza o status de validação da chave.
        
        Args:
            status: Novo status de validação
            error_message: Mensagem de erro (se houver)
        """
        valid_statuses = ['valid', 'invalid', 'expired', 'rate_limited', 'unknown']
        if status not in valid_statuses:
            raise ValueError(f"Invalid validation status. Must be one of: {valid_statuses}")
        
        self.validation_status = status
        self.last_validated_at = datetime.utcnow()
        
        if status == 'valid':
            self.reset_error_count()
            self.activate()
        elif status in ['invalid', 'expired']:
            self.increment_error_count()
            self.deactivate()
        
        # Atualizar estatísticas
        if self.usage_stats is None:
            self.usage_stats = {}
        
        self.usage_stats['last_validation'] = {
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'error_message': error_message
        }
    
    def set_expiration(self, days: int) -> None:
        """
        Define a expiração da chave.
        
        Args:
            days: Número de dias até a expiração
        """
        from datetime import timedelta
        self.expires_at = datetime.utcnow() + timedelta(days=days)
    
    def extend_expiration(self, days: int) -> None:
        """
        Estende a expiração da chave.
        
        Args:
            days: Número de dias para estender
        """
        from datetime import timedelta
        if self.expires_at is None:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        else:
            self.expires_at += timedelta(days=days)
    
    def add_usage_limit(self, limit_type: str, limit_value: int) -> None:
        """
        Adiciona um limite de uso à chave.
        
        Args:
            limit_type: Tipo de limite (daily, monthly, etc.)
            limit_value: Valor do limite
        """
        if self.usage_limits is None:
            self.usage_limits = {}
        
        self.usage_limits[limit_type] = limit_value
    
    def check_usage_limit(self, limit_type: str) -> bool:
        """
        Verifica se um limite de uso foi atingido.
        
        Args:
            limit_type: Tipo de limite a verificar
            
        Returns:
            True se o limite foi atingido
        """
        if self.usage_limits is None or limit_type not in self.usage_limits:
            return False
        
        limit_value = self.usage_limits[limit_type]
        
        # Verificar uso atual (implementação simplificada)
        if self.usage_stats and f'{limit_type}_usage' in self.usage_stats:
            current_usage = self.usage_stats[f'{limit_type}_usage']
            return current_usage >= limit_value
        
        return False
    
    def get_provider_name(self) -> Optional[str]:
        """Retorna o nome do provedor da chave."""
        if self.provider_ref:
            return self.provider_ref.provider_name
        return self.provider
    
    def mask_key_for_display(self) -> str:
        """Retorna uma versão mascarada da chave para exibição."""
        if len(self.key_hash) >= 8:
            return f"****{self.key_hash[-4:]}"
        return "****"
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Converte a chave para dicionário.
        
        Args:
            include_sensitive: Se True, inclui dados sensíveis
            
        Returns:
            Dicionário com os dados da chave
        """
        exclude = {'encrypted_key', 'key_hash'} if not include_sensitive else set()
        data = super().to_dict(exclude=exclude)
        
        # Adicionar propriedades computadas
        data.update({
            'is_valid': self.is_valid,
            'is_expired': self.is_expired,
            'has_errors': self.has_errors,
            'needs_validation': self.needs_validation,
            'usage_count': self.usage_count,
            'provider_name': self.get_provider_name(),
            'masked_key': self.mask_key_for_display()
        })
        
        return data
    
    def __repr__(self) -> str:
        """Representação string da chave de API."""
        return f"<APIKey(id={self.id}, provider='{self.provider}', user_id={self.user_id})>"

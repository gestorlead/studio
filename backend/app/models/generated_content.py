"""
GestorLead Studio - GeneratedContent ORM Model
Task 1.7: Implement SQLAlchemy ORM Models

Modelo de conteúdo gerado pelas tarefas de IA.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, JSON, BigInteger, Numeric,
    ForeignKey, CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base, TimestampMixin
from ..models.entity_types import ContentType, StorageProvider


class GeneratedContent(Base, TimestampMixin):
    """
    Modelo de conteúdo gerado do sistema GestorLead Studio.
    
    Armazena conteúdo gerado pelas tarefas de IA, incluindo metadados
    e referências para arquivos.
    """
    __tablename__ = "generated_content"
    
    # Primary Key (UUID)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign Keys
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('tasks.id'), unique=True, nullable=False,
        doc="Tarefa que gerou o conteúdo"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False, index=True,
        doc="Proprietário do conteúdo"
    )
    
    # Content type and format
    content_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
        doc="Tipo do conteúdo"
    )
    mime_type: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        doc="MIME type do arquivo"
    )
    
    # File information
    file_size_bytes: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        doc="Tamanho do arquivo em bytes"
    )
    file_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
        doc="URL do arquivo armazenado"
    )
    thumbnail_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
        doc="URL da thumbnail (para imagens/vídeos)"
    )
    original_filename: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
        doc="Nome original do arquivo"
    )
    
    # Storage information
    storage_path: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
        doc="Caminho no sistema de storage"
    )
    storage_provider: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
        doc="Provedor de storage (minio, s3, etc.)"
    )
    
    # Content data
    content_text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        doc="Conteúdo textual (para textos gerados)"
    )
    content_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Metadados específicos do conteúdo"
    )
    processing_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Metadados do processamento"
    )
    
    # Quality and organization
    quality_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2), nullable=True,
        doc="Score de qualidade (0.00-10.00)"
    )
    is_favorite: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        doc="Marcado como favorito"
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        doc="Conteúdo público"
    )
    download_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
        doc="Número de downloads"
    )
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        doc="Tags para organização"
    )
    
    # Expiration
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        doc="Data de expiração do conteúdo"
    )
    
    # ===== RELATIONSHIPS =====
    
    # Task relationship (1:1)
    task: Mapped["Task"] = relationship("Task", back_populates="generated_content")
    
    # User relationship (N:1)
    user: Mapped["User"] = relationship("User", back_populates="generated_content")
    
    # ===== CONSTRAINTS AND INDEXES =====
    
    __table_args__ = (
        # Unique constraints
        UniqueConstraint('task_id', name='uq_generated_content_task_id'),
        
        # Check constraints
        CheckConstraint(
            "content_type IN ('text', 'image', 'audio', 'video', 'document', 'data')",
            name='valid_content_type'
        ),
        CheckConstraint(
            "storage_provider IN ('minio', 's3', 'gcs', 'azure_blob', 'local') OR storage_provider IS NULL",
            name='valid_storage_provider'
        ),
        CheckConstraint('file_size_bytes IS NULL OR file_size_bytes > 0', name='file_size_positive'),
        CheckConstraint(
            'quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 10)',
            name='quality_score_valid'
        ),
        CheckConstraint('download_count >= 0', name='download_count_non_negative'),
        CheckConstraint('expires_at IS NULL OR expires_at > created_at', name='expires_after_created'),
        
        # Performance indexes
        Index('idx_generated_content_user_id', 'user_id'),
        Index('idx_generated_content_type', 'content_type'),
        Index('idx_generated_content_task_id', 'task_id'),
        Index('idx_generated_content_user_type', 'user_id', 'content_type'),
        Index('idx_generated_content_public', 'is_public'),
        Index('idx_generated_content_favorite', 'is_favorite'),
    )
    
    # ===== HYBRID PROPERTIES =====
    
    @hybrid_property
    def is_text_content(self) -> bool:
        """Verifica se é conteúdo textual."""
        return self.content_type == 'text'
    
    @hybrid_property
    def is_media_content(self) -> bool:
        """Verifica se é conteúdo de mídia (imagem, áudio, vídeo)."""
        return self.content_type in ('image', 'audio', 'video')
    
    @hybrid_property
    def has_file(self) -> bool:
        """Verifica se tem arquivo associado."""
        return self.file_url is not None and self.file_url.strip() != ''
    
    @hybrid_property
    def has_thumbnail(self) -> bool:
        """Verifica se tem thumbnail disponível."""
        return self.thumbnail_url is not None and self.thumbnail_url.strip() != ''
    
    @hybrid_property
    def is_expired(self) -> bool:
        """Verifica se o conteúdo expirou."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @hybrid_property
    def file_size_mb(self) -> Optional[float]:
        """Retorna o tamanho do arquivo em megabytes."""
        if self.file_size_bytes is None:
            return None
        return round(self.file_size_bytes / 1024 / 1024, 2)
    
    @hybrid_property
    def quality_percentage(self) -> Optional[float]:
        """Retorna o score de qualidade como porcentagem."""
        if self.quality_score is None:
            return None
        return float(self.quality_score) * 10  # Score 0-10 -> 0%-100%
    
    # ===== METHODS =====
    
    def mark_as_favorite(self) -> None:
        """Marca o conteúdo como favorito."""
        self.is_favorite = True
    
    def unmark_as_favorite(self) -> None:
        """Remove a marcação de favorito."""
        self.is_favorite = False
    
    def make_public(self) -> None:
        """Torna o conteúdo público."""
        self.is_public = True
    
    def make_private(self) -> None:
        """Torna o conteúdo privado."""
        self.is_public = False
    
    def increment_download_count(self) -> None:
        """Incrementa o contador de downloads."""
        self.download_count += 1
    
    def set_expiration(self, days: int) -> None:
        """
        Define a expiração do conteúdo.
        
        Args:
            days: Número de dias até a expiração
        """
        from datetime import timedelta
        self.expires_at = datetime.utcnow() + timedelta(days=days)
    
    def extend_expiration(self, days: int) -> None:
        """
        Estende a expiração do conteúdo.
        
        Args:
            days: Número de dias para estender
        """
        from datetime import timedelta
        if self.expires_at is None:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        else:
            self.expires_at += timedelta(days=days)
    
    def add_tag(self, tag: str) -> None:
        """
        Adiciona uma tag ao conteúdo.
        
        Args:
            tag: Tag a ser adicionada
        """
        if self.tags is None:
            self.tags = []
        
        if isinstance(self.tags, list):
            if tag not in self.tags:
                self.tags.append(tag)
        elif isinstance(self.tags, dict):
            # Se tags for um dict, converter para lista
            tag_list = list(self.tags.keys()) if self.tags else []
            if tag not in tag_list:
                tag_list.append(tag)
            self.tags = tag_list
    
    def remove_tag(self, tag: str) -> None:
        """
        Remove uma tag do conteúdo.
        
        Args:
            tag: Tag a ser removida
        """
        if self.tags is None:
            return
        
        if isinstance(self.tags, list):
            if tag in self.tags:
                self.tags.remove(tag)
        elif isinstance(self.tags, dict):
            if tag in self.tags:
                del self.tags[tag]
    
    def get_tag_list(self) -> list:
        """Retorna a lista de tags."""
        if self.tags is None:
            return []
        
        if isinstance(self.tags, list):
            return self.tags
        elif isinstance(self.tags, dict):
            return list(self.tags.keys())
        
        return []
    
    def update_quality_score(self, score: float) -> None:
        """
        Atualiza o score de qualidade.
        
        Args:
            score: Score de qualidade (0.0-10.0)
        """
        if 0.0 <= score <= 10.0:
            self.quality_score = Decimal(str(score)).quantize(Decimal('0.01'))
        else:
            raise ValueError("Quality score must be between 0.0 and 10.0")
    
    def get_display_name(self) -> str:
        """Retorna um nome para exibição do conteúdo."""
        if self.original_filename:
            return self.original_filename
        elif self.content_type == 'text' and self.content_text:
            # Para texto, usar as primeiras palavras como nome
            words = self.content_text.split()[:5]
            return ' '.join(words) + ('...' if len(words) == 5 else '')
        else:
            return f"{self.content_type.title()} Content"
    
    def to_dict(self, include_content: bool = True) -> Dict[str, Any]:
        """
        Converte o conteúdo para dicionário.
        
        Args:
            include_content: Se True, inclui content_text e metadados
            
        Returns:
            Dicionário com os dados do conteúdo
        """
        exclude = set()
        if not include_content:
            exclude.update({'content_text', 'content_metadata', 'processing_metadata'})
        
        data = super().to_dict(exclude=exclude)
        
        # Adicionar propriedades computadas
        data.update({
            'is_text_content': self.is_text_content,
            'is_media_content': self.is_media_content,
            'has_file': self.has_file,
            'has_thumbnail': self.has_thumbnail,
            'is_expired': self.is_expired,
            'file_size_mb': self.file_size_mb,
            'quality_percentage': self.quality_percentage,
            'tag_list': self.get_tag_list(),
            'display_name': self.get_display_name()
        })
        
        return data
    
    def __repr__(self) -> str:
        """Representação string do conteúdo gerado."""
        return f"<GeneratedContent(id={self.id}, type='{self.content_type}', task_id={self.task_id})>"

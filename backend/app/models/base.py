"""
GestorLead Studio - SQLAlchemy Base Model
Task 1.7: Implement SQLAlchemy ORM Models

Classe base para todos os modelos SQLAlchemy com configurações e funcionalidades comuns.
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Classe base para todos os modelos SQLAlchemy.
    
    Fornece funcionalidades comuns como:
    - Timestamps automáticos (created_at, updated_at)
    - Serialização para dicionário
    - Representação string padrão
    """
    
    # Configurações de nomenclatura automática
    __table_args__ = {'mysql_engine': 'InnoDB'} if False else {}
    
    def to_dict(self, exclude: set = None) -> Dict[str, Any]:
        """
        Converte o modelo para dicionário.
        
        Args:
            exclude: Conjunto de campos a serem excluídos
            
        Returns:
            Dicionário com os dados do modelo
        """
        exclude = exclude or set()
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name not in exclude
        }
    
    def update_from_dict(self, data: Dict[str, Any], exclude: set = None) -> None:
        """
        Atualiza o modelo a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados para atualizar
            exclude: Conjunto de campos a serem excluídos da atualização
        """
        exclude = exclude or {'id', 'created_at', 'updated_at'}
        
        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """Representação string padrão do modelo."""
        class_name = self.__class__.__name__
        if hasattr(self, 'id'):
            return f"<{class_name}(id={self.id})>"
        return f"<{class_name}()>"


class TimestampMixin:
    """
    Mixin para adicionar timestamps automáticos aos modelos.
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Data de criação do registro"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Data de última atualização do registro"
    )

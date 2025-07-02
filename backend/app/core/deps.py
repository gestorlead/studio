"""
FastAPI Dependencies
Task: 1.8 - Integrate ORM Models with FastAPI
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.core.config import get_settings

settings = get_settings()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados.
    Garante que a sessão seja fechada após cada request.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        db.close()


def get_current_user_id() -> Optional[int]:
    """
    Dependency para obter ID do usuário atual.
    TODO: Implementar autenticação JWT completa.
    """
    # Placeholder - será implementado com autenticação JWT
    return 1


class CommonQueryParams:
    """Parâmetros comuns de query para paginação e filtros"""
    
    def __init__(
        self,
        skip: int = 0,
        limit: int = settings.DEFAULT_PAGE_SIZE,
        q: Optional[str] = None
    ):
        self.skip = max(0, skip)
        self.limit = min(limit, settings.MAX_PAGE_SIZE)
        self.q = q


def common_parameters(
    skip: int = 0,
    limit: int = settings.DEFAULT_PAGE_SIZE,
    q: Optional[str] = None
) -> CommonQueryParams:
    """Dependency para parâmetros comuns de consulta"""
    return CommonQueryParams(skip=skip, limit=limit, q=q) 
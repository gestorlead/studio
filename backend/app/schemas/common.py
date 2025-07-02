"""
Common Pydantic Schemas
Task: 1.8 - Integrate ORM Models with FastAPI
"""

from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada padrão"""
    items: List[T]
    total: int
    page: int = Field(ge=1, description="Número da página atual")
    per_page: int = Field(ge=1, le=100, description="Itens por página")
    pages: int = Field(ge=1, description="Total de páginas")
    has_prev: bool = Field(description="Tem página anterior")
    has_next: bool = Field(description="Tem próxima página")
    
    @classmethod
    def create(
        cls, 
        items: List[T], 
        total: int, 
        page: int, 
        per_page: int
    ) -> "PaginatedResponse[T]":
        """Criar resposta paginada"""
        pages = (total + per_page - 1) // per_page
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
            has_prev=page > 1,
            has_next=page < pages
        )


class SuccessResponse(BaseModel):
    """Resposta de sucesso padrão"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Resposta de erro padrão"""
    success: bool = False
    error: str
    details: Optional[str] = None
    code: Optional[str] = None


class TimestampMixin(BaseModel):
    """Mixin para campos de timestamp"""
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class BaseSchema(BaseModel):
    """Schema base com configurações padrões"""
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 
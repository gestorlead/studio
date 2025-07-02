"""
User Pydantic Schemas
Task: 1.8 - Integrate ORM Models with FastAPI
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from .common import BaseSchema, TimestampMixin


class UserBase(BaseModel):
    """Schema base do usuário"""
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema para criação de usuário"""
    google_id: Optional[str] = None
    subscription_tier_id: int = Field(default=1, description="ID do plano de assinatura")


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None
    subscription_tier_id: Optional[int] = None


class UserInDB(UserBase, TimestampMixin):
    """Schema do usuário no banco de dados"""
    id: int
    google_id: Optional[str] = None
    credit_balance: int = 0
    subscription_tier_id: int
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class UserResponse(BaseSchema):
    """Schema de resposta do usuário"""
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    credit_balance: int
    subscription_tier_id: int
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Campos calculados
    is_verified: bool = Field(description="Se o email foi verificado")
    has_credits: bool = Field(description="Se tem créditos disponíveis")
    
    class Config:
        orm_mode = True


class UserSummary(BaseModel):
    """Schema resumido do usuário"""
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    credit_balance: int
    
    class Config:
        orm_mode = True


class UserCreditUpdate(BaseModel):
    """Schema para atualização de créditos"""
    credits: int = Field(description="Quantidade de créditos (positivo para adicionar, negativo para debitar)")
    reason: Optional[str] = Field(description="Motivo da alteração de créditos") 
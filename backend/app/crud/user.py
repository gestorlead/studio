"""
User CRUD Operations
Task: 1.8 - Integrate ORM Models with FastAPI
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations para User"""
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        return db.query(User).filter(User.email == email).first()
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Buscar usuário por email (async)"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    def get_by_google_id(self, db: Session, *, google_id: str) -> Optional[User]:
        """Buscar usuário por Google ID"""
        return db.query(User).filter(User.google_id == google_id).first()
    
    async def get_by_google_id(self, db: AsyncSession, *, google_id: str) -> Optional[User]:
        """Buscar usuário por Google ID (async)"""
        result = await db.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()
    
    def update_credits(self, db: Session, *, user: User, credits: int) -> User:
        """Atualizar créditos do usuário"""
        user.credits_balance += credits
        if user.credits_balance < 0:
            user.credits_balance = 0
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def verify_email(self, db: Session, *, user: User) -> User:
        """Marcar email como verificado"""
        from datetime import datetime
        user.email_verified_at = datetime.utcnow()
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def update_last_login(self, db: Session, *, user_id: int) -> Optional[User]:
        """Atualizar último login"""
        from datetime import datetime
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login_at = datetime.utcnow()
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    async def update_last_login(self, db: AsyncSession, *, user_id: int) -> Optional[User]:
        """Atualizar último login (async)"""
        from datetime import datetime
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.last_login_at = datetime.utcnow()
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user
    
    def get_active_users(self, db: Session, *, skip: int = 0, limit: int = 100):
        """Buscar usuários ativos"""
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()


# Instâncias globais do CRUD
crud_user = CRUDUser(User)
user_crud = crud_user  # Alias para compatibilidade

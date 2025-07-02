"""
User Endpoints
Task: 1.8 - Integrate ORM Models with FastAPI
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, common_parameters, CommonQueryParams
from app.crud import crud_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserSummary, UserCreditUpdate
from app.schemas.common import PaginatedResponse, SuccessResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserSummary])
def read_users(
    commons: CommonQueryParams = Depends(common_parameters),
    db: Session = Depends(get_db)
):
    """Listar usuários com paginação"""
    users = crud_user.get_multi(db, skip=commons.skip, limit=commons.limit)
    total = crud_user.count(db)
    
    return PaginatedResponse.create(
        items=users,
        total=total,
        page=(commons.skip // commons.limit) + 1,
        per_page=commons.limit
    )


@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Buscar usuário por ID"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Criar novo usuário"""
    # Verificar se email já existe
    existing_user = crud_user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    user = crud_user.create(db, obj_in=user_in)
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar usuário"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    user = crud_user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=SuccessResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Deletar usuário"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    crud_user.remove(db, id=user_id)
    return SuccessResponse(message="Usuário deletado com sucesso")


@router.post("/{user_id}/credits", response_model=UserResponse)
def update_user_credits(
    user_id: int,
    credit_update: UserCreditUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar créditos do usuário"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    user = crud_user.update_credits(db, user=user, credits=credit_update.credits)
    return user


@router.post("/{user_id}/verify-email", response_model=UserResponse)
def verify_user_email(user_id: int, db: Session = Depends(get_db)):
    """Verificar email do usuário"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    user = crud_user.verify_email(db, user=user)
    return user 
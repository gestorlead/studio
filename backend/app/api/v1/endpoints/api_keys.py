"""API Key Endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user_id
from app.crud import crud_api_key
from app.schemas.api_key import APIKeyCreate, APIKeyResponse

router = APIRouter()

@router.get("/", response_model=list[APIKeyResponse])
def read_api_keys(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return crud_api_key.get_multi(db, skip=skip, limit=limit, user_id=current_user_id)

@router.post("/", response_model=APIKeyResponse)
def create_api_key(api_key_in: APIKeyCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return crud_api_key.create(db, obj_in=api_key_in, user_id=current_user_id) 
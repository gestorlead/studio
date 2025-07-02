"""Generated Content Endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.crud import crud_generated_content
from app.schemas.generated_content import GeneratedContentResponse

router = APIRouter()

@router.get("/", response_model=list[GeneratedContentResponse])
def read_generated_content(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud_generated_content.get_multi(db, skip=skip, limit=limit) 
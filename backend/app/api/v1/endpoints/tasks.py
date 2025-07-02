"""Task Endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user_id
from app.crud import crud_task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[TaskResponse])
def read_tasks(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    tasks = crud_task.get_multi(db, skip=skip, limit=limit, user_id=current_user_id)
    total = crud_task.count(db, user_id=current_user_id)
    return PaginatedResponse.create(items=tasks, total=total, page=(skip // limit) + 1, per_page=limit)

@router.post("/", response_model=TaskResponse)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return crud_task.create(db, obj_in=task_in, user_id=current_user_id)

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: str, db: Session = Depends(get_db)):
    task = crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task 
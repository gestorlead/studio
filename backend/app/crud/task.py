"""Task CRUD Operations"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def get_by_status(self, db: Session, *, status: str, user_id: Optional[int] = None) -> List[Task]:
        query = db.query(Task).filter(Task.status == status)
        if user_id:
            query = query.filter(Task.user_id == user_id)
        return query.all()
    
    def get_by_campaign(self, db: Session, *, campaign_id: str) -> List[Task]:
        return db.query(Task).filter(Task.campaign_id == campaign_id).all()

crud_task = CRUDTask(Task) 
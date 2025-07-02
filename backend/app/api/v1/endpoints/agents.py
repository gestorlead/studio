"""Agent Endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user_id
from app.crud import crud_agent
from app.schemas.agent import AgentCreate, AgentResponse

router = APIRouter()

@router.get("/", response_model=list[AgentResponse])
def read_agents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud_agent.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=AgentResponse)
def create_agent(agent_in: AgentCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return crud_agent.create(db, obj_in=agent_in, user_id=current_user_id) 
"""Agent CRUD Operations"""
from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate

class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    def get_public_agents(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Agent]:
        return db.query(Agent).filter(Agent.is_public == True).offset(skip).limit(limit).all()
    
    def get_by_category(self, db: Session, *, category_id: int) -> List[Agent]:
        return db.query(Agent).filter(Agent.category_id == category_id).all()

crud_agent = CRUDAgent(Agent) 
# Instâncias globais do CRUD
crud_agent = CRUDAgent(Agent)  
agent_crud = crud_agent

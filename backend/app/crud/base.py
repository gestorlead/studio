"""
Base CRUD Operations
Task: 1.8 - Integrate ORM Models with FastAPI
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """CRUD base genérico para operações comuns"""
    
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        **Parameters**
        * `model`: SQLAlchemy model class
        * `schema`: Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Buscar por ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        user_id: Optional[int] = None
    ) -> List[ModelType]:
        """Buscar múltiplos registros com paginação"""
        query = db.query(self.model)
        
        # Filtrar por usuário se aplicável
        if user_id is not None and hasattr(self.model, 'user_id'):
            query = query.filter(self.model.user_id == user_id)
        
        return query.offset(skip).limit(limit).all()

    def count(self, db: Session, user_id: Optional[int] = None) -> int:
        """Contar total de registros"""
        query = db.query(func.count(self.model.id))
        
        if user_id is not None and hasattr(self.model, 'user_id'):
            query = query.filter(self.model.user_id == user_id)
        
        return query.scalar()

    def create(self, db: Session, *, obj_in: CreateSchemaType, user_id: Optional[int] = None) -> ModelType:
        """Criar novo registro"""
        obj_in_data = jsonable_encoder(obj_in)
        
        # Adicionar user_id se fornecido e o modelo suportar
        if user_id is not None and hasattr(self.model, 'user_id'):
            obj_in_data["user_id"] = user_id
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Atualizar registro existente"""
        obj_data = jsonable_encoder(db_obj)
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """Remover registro"""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_field(self, db: Session, field: str, value: Any) -> Optional[ModelType]:
        """Buscar por campo específico"""
        return db.query(self.model).filter(getattr(self.model, field) == value).first()

    def search(
        self, 
        db: Session, 
        query: str, 
        fields: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Busca textual em múltiplos campos"""
        filters = []
        for field in fields:
            if hasattr(self.model, field):
                filters.append(getattr(self.model, field).ilike(f"%{query}%"))
        
        if not filters:
            return []
        
        # Combinar filtros com OR
        from sqlalchemy import or_
        return db.query(self.model).filter(or_(*filters)).offset(skip).limit(limit).all() 
"""API Key CRUD Operations"""
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate

class CRUDAPIKey(CRUDBase[APIKey, APIKeyCreate, dict]):
    pass

crud_api_key = CRUDAPIKey(APIKey) 
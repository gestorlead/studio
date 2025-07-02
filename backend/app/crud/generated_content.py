"""Generated Content CRUD Operations"""
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.generated_content import GeneratedContent
from app.schemas.generated_content import GeneratedContentResponse

class CRUDGeneratedContent(CRUDBase[GeneratedContent, dict, dict]):
    pass

crud_generated_content = CRUDGeneratedContent(GeneratedContent) 
"""API Key Pydantic Schemas"""
from typing import Optional
from pydantic import BaseModel, UUID4
from datetime import datetime
from .common import BaseSchema

class APIKeyCreate(BaseModel):
    provider_id: int
    key_name: str
    encrypted_key: str

class APIKeyResponse(BaseSchema):
    id: UUID4
    user_id: int
    provider_id: int
    key_name: str
    masked_key: str
    is_active: bool
    is_default: bool
    is_validated: bool
    validation_status: Optional[str]
    error_count: int
    last_used_at: Optional[datetime]
    last_validated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime 
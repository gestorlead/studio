"""
API Keys model for GestorLead Studio
Based on Task 1.1 - Define Entity Models and Attributes
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModel

class APIKey(Base, BaseModel):
    """API keys model for secure provider key storage"""
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    
    # Legacy field for compatibility
    provider = Column(String(50), nullable=True, index=True)
    
    key_name = Column(String(100), nullable=False)
    encrypted_key = Column(Text, nullable=False)
    key_hash = Column(String(64), nullable=False)  # SHA-256 hash
    permissions = Column(JSON, nullable=True)
    usage_limits = Column(JSON, nullable=True)
    usage_stats = Column(JSON, nullable=True)
    
    is_active = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    last_validated_at = Column(DateTime, nullable=True)
    validation_status = Column(String(20), nullable=True)  # valid, invalid, expired, rate_limited, unknown
    error_count = Column(Integer, nullable=False, default=0)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    provider_rel = relationship("AIProvider", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey(id='{self.id}', provider='{self.provider}')>"

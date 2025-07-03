"""
Authentication schemas for request/response validation
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth authentication"""
    code: str
    state: Optional[str] = None


class TokenResponse(BaseModel):
    """Response model for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str


class AuthURLResponse(BaseModel):
    """Response model for OAuth authorization URL"""
    auth_url: str
    state: Optional[str] = None


class LogoutResponse(BaseModel):
    """Response model for logout"""
    message: str = "Successfully logged out"


class AuthUserResponse(BaseModel):
    """User information in auth responses"""
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    credits_balance: float
    
    class Config:
        from_attributes = True

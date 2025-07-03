"""
Authentication endpoints for Google OAuth and JWT management
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.auth.service import AuthService
from app.auth.dependencies import get_current_active_user, get_auth_service
from app.schemas.auth import (
    GoogleAuthRequest,
    TokenResponse,
    RefreshTokenRequest,
    AuthURLResponse,
    LogoutResponse,
    AuthUserResponse
)
from app.models.user import User
from app.core.security import verify_token


router = APIRouter()


@router.get("/google/url", response_model=AuthURLResponse)
async def get_google_auth_url(
    state: Annotated[str, Query(description="State parameter for CSRF protection")] = None,
    auth_service: Annotated[AuthService, Depends(get_auth_service)] = None
):
    """
    Get Google OAuth authorization URL
    
    Args:
        state: Optional state parameter for CSRF protection
        auth_service: Authentication service
        
    Returns:
        Authorization URL for Google OAuth
    """
    auth_url = auth_service.get_google_auth_url(state)
    return AuthURLResponse(auth_url=auth_url, state=state)


@router.post("/google/callback", response_model=TokenResponse)
async def google_oauth_callback(
    auth_request: GoogleAuthRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Handle Google OAuth callback and authenticate user
    
    Args:
        auth_request: Google OAuth callback data
        db: Database session
        auth_service: Authentication service
        
    Returns:
        JWT tokens and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    result = await auth_service.authenticate_with_google(
        code=auth_request.code,
        db=db
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authentication failed"
        )
    
    user = result["user"]
    tokens = result["tokens"]
    
    # Convert user to response format
    user_data = AuthUserResponse.from_orm(user)
    
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
        user=user_data.dict()
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Refresh access token using refresh token
    
    Args:
        refresh_request: Refresh token request
        db: Database session
        auth_service: Authentication service
        
    Returns:
        New JWT tokens
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    tokens = await auth_service.refresh_access_token(
        refresh_token=refresh_request.refresh_token,
        db=db
    )
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user info for response
    token_data = verify_token(refresh_request.refresh_token, "refresh")
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    from app.crud.user import user_crud
    user = await user_crud.get(db, id=token_data.user_id)
    user_data = AuthUserResponse.from_orm(user)
    
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
        user=user_data.dict()
    )


@router.get("/me", response_model=AuthUserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get current authenticated user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return AuthUserResponse.from_orm(current_user)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Logout current user
    
    Args:
        current_user: Current authenticated user
        db: Database session
        auth_service: Authentication service
        
    Returns:
        Logout confirmation
    """
    success = await auth_service.logout_user(
        user_id=current_user.id,
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )
    
    return LogoutResponse()


@router.get("/verify", response_model=dict)
async def verify_token(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Verify if current token is valid
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Token verification status
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email
    }

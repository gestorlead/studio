"""
FastAPI dependencies for authentication
"""
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.auth.service import AuthService
from app.models.user import User


# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_auth_service() -> AuthService:
    """Get authentication service instance"""
    return AuthService()


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Optional[User]:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        auth_service: Authentication service
        
    Returns:
        User object or None if not authenticated
    """
    if not credentials:
        return None
    
    try:
        user = await auth_service.get_current_user(
            access_token=credentials.credentials,
            db=db
        )
        return user
    except Exception:
        return None


async def get_current_active_user(
    current_user: Annotated[Optional[User], Depends(get_current_user)]
) -> User:
    """
    Get current active user (raises exception if not authenticated)
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is not authenticated or not active
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Get current verified user
    
    Args:
        current_user: Current active user
        
    Returns:
        Verified user object
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    
    return current_user


def require_scopes(required_scopes: list[str]):
    """
    Dependency factory for requiring specific scopes
    
    Args:
        required_scopes: List of required permission scopes
        
    Returns:
        FastAPI dependency function
    """
    async def check_scopes(
        current_user: Annotated[User, Depends(get_current_active_user)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
    ) -> User:
        """Check if user has required scopes"""
        has_permission = await auth_service.verify_user_permissions(
            user=current_user,
            required_scopes=required_scopes
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return current_user
    
    return check_scopes


# Common permission dependencies
require_user_scope = require_scopes(["user"])
require_admin_scope = require_scopes(["admin"])

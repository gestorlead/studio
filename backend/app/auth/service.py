"""
Authentication service for user management and JWT handling
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import create_token_pair, verify_token, Token
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.oauth import GoogleOAuth


class AuthService:
    """Authentication service for managing user sessions and tokens"""
    
    def __init__(self):
        self.google_oauth = GoogleOAuth()
    
    async def authenticate_with_google(
        self, 
        code: str, 
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with Google OAuth
        
        Args:
            code: OAuth authorization code
            db: Database session
            
        Returns:
            Authentication result with user and tokens
        """
        # Get user info from Google
        auth_result = await self.google_oauth.authenticate_user(code)
        if not auth_result:
            return None
        
        user_info = auth_result["user_info"]
        email = user_info.get("email")
        
        if not email:
            return None
        
        # Check if user exists
        existing_user = await user_crud.get_by_email(db, email=email)
        
        if existing_user:
            # Update last login
            await user_crud.update_last_login(db, user_id=existing_user.id)
            user = existing_user
        else:
            # Create new user
            user_data = UserCreate(
                email=email,
                full_name=user_info.get("name", ""),
                google_id=user_info.get("id"),
                avatar_url=user_info.get("picture"),
                is_active=True,
                is_verified=True  # Google users are pre-verified
            )
            user = await user_crud.create(db, obj_in=user_data)
        
        # Create JWT tokens
        tokens = create_token_pair(
            user_id=user.id,
            email=user.email,
            scopes=["user"]  # Basic user scope
        )
        
        return {
            "user": user,
            "tokens": tokens,
            "google_tokens": auth_result["tokens"]
        }
    
    async def refresh_access_token(
        self, 
        refresh_token: str, 
        db: AsyncSession
    ) -> Optional[Token]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: JWT refresh token
            db: Database session
            
        Returns:
            New token pair or None if invalid
        """
        # Verify refresh token
        token_data = verify_token(refresh_token, token_type="refresh")
        if not token_data:
            return None
        
        # Check if user still exists and is active
        user = await user_crud.get(db, id=token_data.user_id)
        if not user or not user.is_active:
            return None
        
        # Create new token pair
        new_tokens = create_token_pair(
            user_id=user.id,
            email=user.email,
            scopes=token_data.scopes
        )
        
        return new_tokens
    
    async def get_current_user(
        self, 
        access_token: str, 
        db: AsyncSession
    ) -> Optional[User]:
        """
        Get current user from access token
        
        Args:
            access_token: JWT access token
            db: Database session
            
        Returns:
            User object or None if invalid
        """
        # Verify access token
        token_data = verify_token(access_token, token_type="access")
        if not token_data:
            return None
        
        # Get user from database
        user = await user_crud.get(db, id=token_data.user_id)
        if not user or not user.is_active:
            return None
        
        return user
    
    async def logout_user(
        self, 
        user_id: int, 
        db: AsyncSession
    ) -> bool:
        """
        Logout user (invalidate sessions)
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            True if successful
        """
        # In a more complex system, we would invalidate tokens in Redis
        # For now, we just update the user's last activity
        user = await user_crud.get(db, id=user_id)
        if not user:
            return False
        
        # Update last activity
        await user_crud.update_last_login(db, user_id=user_id)
        return True
    
    def get_google_auth_url(self, state: Optional[str] = None) -> str:
        """
        Get Google OAuth authorization URL
        
        Args:
            state: Optional state parameter
            
        Returns:
            Authorization URL
        """
        return self.google_oauth.get_authorization_url(state)
    
    async def verify_user_permissions(
        self, 
        user: User, 
        required_scopes: list[str]
    ) -> bool:
        """
        Verify if user has required permissions
        
        Args:
            user: User object
            required_scopes: Required permission scopes
            
        Returns:
            True if user has permissions
        """
        # Basic implementation - all active users have "user" scope
        # In the future, this can be expanded with role-based permissions
        if not user.is_active:
            return False
        
        # For now, all active users have basic permissions
        user_scopes = ["user"]
        
        # Check if user has all required scopes
        return all(scope in user_scopes for scope in required_scopes)

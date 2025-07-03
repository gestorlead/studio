"""
Google OAuth integration for authentication
"""
import json
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.exceptions

from app.core.config import settings


class GoogleOAuth:
    """Google OAuth authentication service"""
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        
        # OAuth 2.0 endpoints
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        # Scopes for user information
        self.scopes = [
            "openid",
            "email", 
            "profile"
        ]
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate Google OAuth authorization URL
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "access_type": "offline",
            "include_granted_scopes": "true"
        }
        
        if state:
            params["state"] = state
            
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Token response or None if failed
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.token_url, data=data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from Google API
        
        Args:
            access_token: Google access token
            
        Returns:
            User information or None if failed
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.userinfo_url, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None
    
    def verify_id_token(self, id_token_str: str) -> Optional[Dict[str, Any]]:
        """
        Verify Google ID token
        
        Args:
            id_token_str: ID token from Google
            
        Returns:
            Token payload or None if invalid
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                self.client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return None
                
            return idinfo
            
        except google.auth.exceptions.GoogleAuthError:
            return None
    
    async def authenticate_user(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Complete OAuth flow and get user information
        
        Args:
            code: Authorization code from Google
            
        Returns:
            User information with tokens or None if failed
        """
        # Exchange code for tokens
        token_response = await self.exchange_code_for_token(code)
        if not token_response:
            return None
        
        access_token = token_response.get("access_token")
        id_token_str = token_response.get("id_token")
        
        if not access_token:
            return None
        
        # Get user info from API
        user_info = await self.get_user_info(access_token)
        if not user_info:
            return None
        
        # Verify ID token if present
        id_info = None
        if id_token_str:
            id_info = self.verify_id_token(id_token_str)
        
        return {
            "user_info": user_info,
            "id_info": id_info,
            "tokens": token_response
        }
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Google refresh token
            
        Returns:
            New token response or None if failed
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.token_url, data=data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None

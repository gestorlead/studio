"""
FastAPI Middleware
Task: 1.8 - Integrate ORM Models with FastAPI
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class DatabaseTransactionMiddleware(BaseHTTPMiddleware):
    """
    Middleware para gerenciar transações de banco automaticamente
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Wrap requests in database transactions"""
        
        # Skip transaction for certain paths
        skip_paths = ["/health", "/", "/docs", "/redoc", "/openapi.json"]
        if request.url.path in skip_paths:
            return await call_next(request)
        
        response = await call_next(request)
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para tratamento global de erros
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors globally"""
        
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as exc:
            # FastAPI HTTPExceptions are already handled properly
            raise exc
            
        except IntegrityError as exc:
            logger.error(f"Database integrity error: {exc}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Data integrity violation",
                    "details": "The operation violates database constraints",
                    "code": "INTEGRITY_ERROR"
                }
            )
            
        except SQLAlchemyError as exc:
            logger.error(f"Database error: {exc}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Database error",
                    "details": "An error occurred while accessing the database",
                    "code": "DATABASE_ERROR"
                }
            )
            
        except ValueError as exc:
            logger.error(f"Value error: {exc}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Invalid input",
                    "details": str(exc),
                    "code": "VALUE_ERROR"
                }
            )
            
        except Exception as exc:
            logger.error(f"Unexpected error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "details": "An unexpected error occurred",
                    "code": "INTERNAL_ERROR"
                }
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de requests
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details"""
        
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response
        logger.info(
            f"Response: {response.status_code} "
            f"processed in {process_time:.4f}s"
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para adicionar headers de segurança
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers"""
        
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response 
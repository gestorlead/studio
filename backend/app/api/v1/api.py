"""
Main API v1 Router
Task: 1.8 - Integrate ORM Models with FastAPI
"""

from fastapi import APIRouter

from app.api.v1.endpoints import users, tasks, agents, campaigns, generated_content, api_keys

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(generated_content.router, prefix="/content", tags=["generated-content"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"]) 
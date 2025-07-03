"""
CRUD operations for all models
"""

from .user import user_crud, crud_user
from .task import task_crud, crud_task  
from .agent import agent_crud, crud_agent
from .campaign import campaign_crud, crud_campaign
from .generated_content import generated_content_crud, crud_generated_content
from .api_key import api_key_crud, crud_api_key

__all__ = [
    "user_crud", "crud_user",
    "task_crud", "crud_task", 
    "agent_crud", "crud_agent",
    "campaign_crud", "crud_campaign",
    "generated_content_crud", "crud_generated_content",
    "api_key_crud", "crud_api_key"
]

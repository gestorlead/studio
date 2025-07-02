"""Lookup Tables Pydantic Schemas"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from .common import BaseSchema

class SubscriptionTierResponse(BaseSchema):
    id: int
    tier_name: str
    monthly_credits: int
    monthly_price_cents: Optional[int]
    max_agents: Optional[int]
    max_campaigns: Optional[int]
    features: Optional[Dict[str, Any]]
    is_active: bool

class AIProviderResponse(BaseSchema):
    id: int
    provider_name: str
    api_base_url: Optional[str]
    supported_features: Optional[List[str]]
    pricing_model: Optional[str]
    is_active: bool

class TaskTypeResponse(BaseSchema):
    id: int
    type_name: str
    category: str
    base_credit_cost: int
    estimated_duration_minutes: Optional[int]
    required_parameters: Optional[List[str]]
    output_formats: Optional[List[str]]
    description: Optional[str]
    is_active: bool 
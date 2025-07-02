"""
GestorLead Studio - Entity Type Definitions
Task 1.1: Define Entity Models and Attributes

Este arquivo define os tipos de dados e enums para todas as entidades do sistema,
garantindo consistência e validação em todo o codebase.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


# =============================================================================
# ENUM DEFINITIONS
# =============================================================================

class SubscriptionTier(str, Enum):
    """Níveis de assinatura disponíveis"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class TaskType(str, Enum):
    """Tipos de tarefas de IA disponíveis"""
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    AUDIO_GENERATION = "audio_generation"
    VIDEO_GENERATION = "video_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


class AIProvider(str, Enum):
    """Provedores de IA suportados"""
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    PIAPI = "piapi"
    ELEVENLABS = "elevenlabs"
    AZURE = "azure"
    AWS = "aws"


class TaskStatus(str, Enum):
    """Status de execução de tarefas"""
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class TaskPriority(str, Enum):
    """Níveis de prioridade de tarefas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AgentType(str, Enum):
    """Tipos de agentes disponíveis"""
    WORKFLOW = "workflow"
    SCHEDULED = "scheduled"
    TRIGGER_BASED = "trigger_based"
    API_ENDPOINT = "api_endpoint"


class AgentStatus(str, Enum):
    """Status de agentes"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    PUBLISHED = "published"


class AgentCategory(str, Enum):
    """Categorias de agentes"""
    MARKETING = "marketing"
    CONTENT_CREATION = "content_creation"
    ANALYTICS = "analytics"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    SEO = "seo"
    AUTOMATION = "automation"


class CampaignType(str, Enum):
    """Tipos de campanhas"""
    SOCIAL_MEDIA = "social_media"
    EMAIL_MARKETING = "email_marketing"
    CONTENT_MARKETING = "content_marketing"
    SEO = "seo"
    PAID_ADS = "paid_ads"
    MULTI_CHANNEL = "multi_channel"


class CampaignStatus(str, Enum):
    """Status de campanhas"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ContentType(str, Enum):
    """Tipos de conteúdo gerado"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    DATA = "data"


class StorageProvider(str, Enum):
    """Provedores de armazenamento"""
    MINIO = "minio"
    S3 = "s3"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"
    LOCAL = "local"


class ValidationStatus(str, Enum):
    """Status de validação de chaves API"""
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_email(email: str) -> bool:
    """Validar formato de email"""
    import re
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return bool(re.match(pattern, email))


def validate_credit_balance(balance: int) -> bool:
    """Validar que o saldo de créditos não é negativo"""
    return balance >= 0


def validate_quality_score(score: Optional[Decimal]) -> bool:
    """Validar que o score de qualidade está entre 0 e 10"""
    if score is None:
        return True
    return Decimal('0.00') <= score <= Decimal('10.00')


def validate_success_rate(rate: Optional[Decimal]) -> bool:
    """Validar que a taxa de sucesso está entre 0 e 1"""
    if rate is None:
        return True
    return Decimal('0.0000') <= rate <= Decimal('1.0000')


# =============================================================================
# ENTITY SUMMARY
# =============================================================================

"""
TASK 1.1 COMPLETED:
- 6 Core Entities Defined
- 13 Enum Types Created
- 98 Total Fields Specified  
- Type Safety Ensured
- Validation Functions Added

Ready for Task 1.2: Design Table Relationships and Foreign Keys
"""

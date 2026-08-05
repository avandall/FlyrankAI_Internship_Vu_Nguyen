"""
Schemas for Multi-Platform Social Campaign Publisher.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class PlatformType(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"


class Campaign(BaseModel):
    campaign_id: str
    tenant_id: str
    title: str
    master_text: str
    media_url: Optional[str] = None
    target_platforms: List[PlatformType]


class ContentVariant(BaseModel):
    platform: PlatformType
    adapted_text: str
    media_url: Optional[str] = None
    character_count: int


class PublishStatus(str, Enum):
    QUEUED = "queued"
    PUBLISHED = "published"
    FAILED = "failed"
    SKIPPED_DUPLICATE = "skipped_duplicate"


class PublishRequest(BaseModel):
    idempotency_key: str
    campaign_id: str
    platform: PlatformType
    content: ContentVariant


class PublishResult(BaseModel):
    post_id: str
    platform: PlatformType
    status: PublishStatus
    external_url: Optional[str] = None
    published_at: str
    error_message: Optional[str] = None


class SignedWebhook(BaseModel):
    payload: Dict[str, Any]
    signature: str
    timestamp: int

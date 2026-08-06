"""
Pydantic Schemas for Embeddable Widget & Lead-Capture Platform.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Tenant business name")
    email: str = Field(..., description="Tenant email address")
    tenant_id: Optional[str] = Field(None, description="Optional custom tenant ID")


class TenantResponse(BaseModel):
    tenant_id: str
    name: str
    email: str
    api_key: str
    created_at: str


class WidgetCreate(BaseModel):
    widget_id: Optional[str] = Field(None, description="Unique widget ID")
    name: str = Field(..., min_length=1, description="Widget name")
    form_type: str = Field(default="contact", description="contact, signup, cta, popover")
    title: Optional[str] = Field("Get in touch", description="Widget header title")
    description: Optional[str] = Field("", description="Widget description")
    button_text: Optional[str] = Field("Submit", description="CTA button text")
    allowed_domains: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    rate_limit_per_min: int = Field(default=10, ge=1, le=1000)
    webhook_url: Optional[str] = None
    primary_color: str = Field(default="#38BDF8")


class WidgetUpdate(BaseModel):
    name: Optional[str] = None
    form_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    button_text: Optional[str] = None
    allowed_domains: Optional[List[str]] = None
    rate_limit_per_min: Optional[int] = Field(None, ge=1, le=1000)
    webhook_url: Optional[str] = None
    is_active: Optional[bool] = None
    primary_color: Optional[str] = None


class WidgetResponse(BaseModel):
    widget_id: str
    tenant_id: str
    name: str
    form_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    button_text: Optional[str] = None
    allowed_domains: List[str] = Field(default_factory=list)
    rate_limit_per_min: int = 10
    webhook_url: Optional[str] = None
    is_active: bool = True
    primary_color: str = "#38BDF8"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PublicSubmissionRequest(BaseModel):
    widget_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None
    _hp_field: Optional[str] = None

    class Config:
        extra = "allow"


class LeadResponse(BaseModel):
    submission_id: str
    widget_id: str
    tenant_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    source_origin: Optional[str] = None
    source_ip: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    geo_provider: Optional[str] = None
    webhook_status: Optional[str] = None
    submitted_at: Optional[str] = None


def format_db_row(row: dict) -> dict:
    """Helper to convert datetime objects in db dicts to ISO strings."""
    if not row:
        return row
    out = dict(row)
    for k, v in out.items():
        if isinstance(v, datetime):
            out[k] = v.isoformat()
    return out

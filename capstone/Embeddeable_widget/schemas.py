"""
Schemas for Embeddable Widget & Lead-Capture Platform.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class WidgetTheme(BaseModel):
    primary_color: str = "#3B82F6"
    position: str = "bottom-right"  # bottom-right, bottom-left, center
    button_text: str = "Contact Us"


class WidgetConfig(BaseModel):
    widget_id: str = Field(..., description="Unique Widget ID")
    tenant_id: str = Field(..., description="Tenant owner ID")
    name: str = Field(..., description="Widget name")
    allowed_domains: List[str] = Field(default_factory=list, description="Allowed domains for CORS")
    theme: WidgetTheme = Field(default_factory=WidgetTheme)
    fields: List[str] = Field(default_factory=lambda: ["name", "email", "message"])
    is_active: bool = True
    rate_limit_per_min: int = Field(default=5, gt=0)


class LeadSubmission(BaseModel):
    submission_id: str
    widget_id: str
    tenant_id: str
    visitor_email: str
    visitor_name: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    ip_address: str
    geo_country: Optional[str] = "Unknown"
    geo_city: Optional[str] = "Unknown"
    created_at: str


class PublicSubmissionRequest(BaseModel):
    widget_id: str
    visitor_email: str
    visitor_name: Optional[str] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)
    honeypot_field: Optional[str] = None
    origin_domain: str
    client_ip: str


class GeoResult(BaseModel):
    country: str
    city: str
    provider_used: str

"""
Embeddable Widget & Lead-Capture Platform — FastAPI App (Port 8002)
Rebuilt per Capstone Spec:
- Widget CRUD with multi-tenant auth (X-API-Key header)
- /widget.js served as versioned embeddable script
- Public submission endpoint with CORS (cross-origin)
- Geo-IP enrichment fallback (ip-api.com → ipapi.co)
- Rate limiting (429), honeypot spam detection
- Persistent SQLite storage
- Dashboard API for leads + stats
"""

import os
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from capstone.Embeddeable_widget.core.database import init_db
from capstone.Embeddeable_widget.services.tenant import TenantService
from capstone.Embeddeable_widget.services.widget import WidgetService
from capstone.Embeddeable_widget.routers import widget_js, widgets, public, leads, tenants, ui

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Embeddable Widget & Lead-Capture Platform",
    description="Capstone Project 2 — Real widget.js embed, Geo-IP, Multi-tenant, SQLite",
    version="2.0.0",
)

# CORS: allow ALL origins so widget.js works from any external site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Widget-Version"],
)

# Initialize DB and services
init_db()
tenant_svc = TenantService()
widget_svc = WidgetService()

# Seed demo tenant + widget on startup (idempotent)
demo_tenant = tenant_svc.create_tenant("FlyRank Demo", "demo@flyrank.ai", "t_demo")
demo_widget = widget_svc.create_widget("t_demo", {
    "widget_id": "w_demo_flyrank",
    "name": "FlyRank Contact Form",
    "form_type": "contact",
    "title": "Get in touch with FlyRank",
    "description": "Fill in your details and we'll get back to you",
    "button_text": "Send Message",
    "allowed_domains": ["localhost", "127.0.0.1", "flyrank.ai"],
    "rate_limit_per_min": 5,
    "primary_color": "#38BDF8",
})

# Static UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(widget_js.router)
app.include_router(widgets.router)
app.include_router(public.router)
app.include_router(leads.router)
app.include_router(tenants.router)
app.include_router(ui.router)

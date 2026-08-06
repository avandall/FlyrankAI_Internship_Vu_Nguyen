"""
Embeddable Widget & Lead-Capture Platform — FastAPI App
Rebuilt per Capstone Spec:
- Widget CRUD with multi-tenant auth (X-API-Key header)
- /widget.js served as versioned embeddable script
- Public submission endpoint with CORS (cross-origin)
- Geo-IP enrichment fallback (ip-api.com → ipapi.co)
- Rate limiting (429), honeypot spam detection
- Persistent PostgreSQL storage
- Dashboard API for leads + stats
"""

import os
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from capstone.Embeddeable_widget.core.database import init_db, close_db_pool
from capstone.Embeddeable_widget.core.config import WIDGET_API_KEY
from capstone.Embeddeable_widget.services.tenant import TenantService
from capstone.Embeddeable_widget.services.widget import WidgetService
from capstone.Embeddeable_widget.routers import widget_js, widgets, public, leads, tenants, ui

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tenant_svc = TenantService()
widget_svc = WidgetService()

DEMO_KEY = WIDGET_API_KEY or "sk_demo_flyrank_123"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Seed demo tenant + widget on startup with known demo key
    demo_tenant = await tenant_svc.create_tenant("FlyRank Demo", "demo@flyrank.ai", "t_demo", force_api_key=DEMO_KEY)
    # Seed 3 demo widgets representing contact, popover, and signup form types
    await widget_svc.create_widget("t_demo", {
        "widget_id": "w_demo_flyrank",
        "name": "FlyRank Contact Form",
        "form_type": "contact",
        "title": "Get in touch with FlyRank",
        "description": "Fill in your details and we'll get back to you",
        "button_text": "Send Message",
        "allowed_domains": ["localhost", "127.0.0.1", "flyrank.ai"],
        "rate_limit_per_min": 10,
        "primary_color": "#38BDF8",
    })
    await widget_svc.create_widget("t_demo", {
        "widget_id": "w_demo_popover",
        "name": "FlyRank Chat Popover",
        "form_type": "popover",
        "title": "Need help? Chat with us!",
        "description": "Our team is online to answer your questions",
        "button_text": "Start Conversation",
        "allowed_domains": ["localhost", "127.0.0.1", "flyrank.ai"],
        "rate_limit_per_min": 10,
        "primary_color": "#8B5CF6",
    })
    await widget_svc.create_widget("t_demo", {
        "widget_id": "w_demo_signup",
        "name": "FlyRank Newsletter Signup",
        "form_type": "signup",
        "title": "Subscribe to FlyRank Weekly",
        "description": "Get latest AI & SEO updates delivered straight to your inbox",
        "button_text": "Subscribe Now",
        "allowed_domains": ["localhost", "127.0.0.1", "flyrank.ai"],
        "rate_limit_per_min": 10,
        "primary_color": "#10B981",
    })
    yield
    await close_db_pool()

app = FastAPI(
    title="Embeddable Widget & Lead-Capture Platform",
    description="Capstone Project 2 — Real widget.js embed, Geo-IP, Multi-tenant, PostgreSQL",
    version="2.0.0",
    lifespan=lifespan,
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

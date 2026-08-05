"""
Usage Metering & Billing Engine — FastAPI App (Port 8004)
Refactored to Clean Architecture
"""
import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from capstone.Usage_metering.core.database import init_db
from capstone.Usage_metering.services.tenant import TenantService
from capstone.Usage_metering.routers import tenant, usage, stripe, ui

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Usage Metering & Billing Engine",
    description="Capstone Project 4 — Real idempotency, quota 429/402, integer cost calculation, Stripe webhook HMAC",
    version="2.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize
init_db()
tenant_svc = TenantService()

# Seed demo tenants
tenant_svc.create_tenant("FlyRank Demo (Free)", "demo@flyrank.ai", "free", "t_demo_free")
tenant_svc.create_tenant("FlyRank Pro (Pro)", "pro@flyrank.ai", "pro", "t_demo_pro")

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(tenant.router)
app.include_router(usage.router)
app.include_router(stripe.router)
app.include_router(ui.router)

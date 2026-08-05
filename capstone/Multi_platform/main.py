"""
Multi-Platform Social Campaign Publisher — FastAPI App (Port 8003)
Rebuilt per Capstone Spec:
- Campaign creation with image upload
- Image variant pipeline (Pillow: Instagram 1080×1080, Twitter 1600×900)
- Platform-tailored caption generation
- Publishing via adapter layer (Fake Social Platform Server)
- Webhook endpoint with HMAC signature verification
- Campaign status tracking
"""

import os
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from capstone.Multi_platform.core.database import init_db
from capstone.Multi_platform.routers import campaigns, images, captions, webhooks, platforms, ui

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Platform Social Campaign Publisher",
    description="Capstone Project 3 — Pillow image variants, Fake Social Server, HMAC webhooks, Idempotent publishing",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
init_db()

# Static UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(campaigns.router)
app.include_router(images.router)
app.include_router(captions.router)
app.include_router(webhooks.router)
app.include_router(platforms.router)
app.include_router(ui.router)

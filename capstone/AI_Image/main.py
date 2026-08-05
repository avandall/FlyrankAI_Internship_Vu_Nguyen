"""
FastAPI app for AI Image Understanding & Content Matching Engine.
Port 8001. Rebuilt per Capstone Spec with real file upload, persistent DB,
Vision AI pipeline, semantic matching, and Review API.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from capstone.AI_Image.core.database import init_db
from capstone.AI_Image.services.ingestion import ImageIngestionService
from capstone.AI_Image.core.config import SEED_IMAGES
from capstone.AI_Image.routers import ingest, images, jobs, matching, reviews, ui

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Image Understanding & Content Matching Engine",
    description="Capstone Project 1 — Real Vision AI Pipeline + Semantic Matching",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Initialize DB and services ──────────────────────────────────────────────
init_db()
ingestion_svc = ImageIngestionService()

# Seed demo images on startup (idempotent - uses INSERT OR REPLACE)
for seed in SEED_IMAGES:
    ingestion_svc.ingest_metadata(seed)

# Static UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(ingest.router)
app.include_router(images.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(reviews.router)
app.include_router(ui.router)

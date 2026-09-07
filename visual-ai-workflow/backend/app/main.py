"""
FastAPI Main Application for Visual AI Workflow System
"""

import os
from dotenv import load_dotenv
import inngest.fast_api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.workflow_router import router as workflow_router
from app.services.inngest_workflow_service import (
    execute_ai_workflow,
    inngest_client,
)
from app.storage.run_store import init_store

load_dotenv()
init_store()

app = FastAPI(
    title="Visual AI Workflow Builder & Inngest Engine",
    description="Interactive node-based AI decision workflow powered by Inngest, React Flow, and Groq LLM.",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(workflow_router)

# Mount Inngest Endpoint
inngest.fast_api.serve(app, inngest_client, [execute_ai_workflow])


@app.get("/health")
def health():
    return {"status": "ok", "app": "Visual AI Workflow", "inngest_mounted": True}


# Mount Frontend Dist if built
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../frontend/dist"))
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
else:
    @app.get("/")
    def index():
        return {
            "message": "Visual AI Workflow API is running",
            "docs_url": "/docs",
            "inngest_endpoint": "/api/inngest",
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

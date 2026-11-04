import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.database.session import init_db
from backend.app.api.endpoints import videos, processing, dashboard, settings as settings_endpoint, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite tables on startup
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Computer Vision Backend for Honeybee Entrance Activity Monitoring, Directional Counting, and Anomaly Tracking.",
    lifespan=lifespan
)

# Enable CORS for frontend Vite development and local deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount storage directory for video previews and annotated video playback
app.mount("/storage", StaticFiles(directory=str(settings.STORAGE_DIR)), name="storage")

# Include API endpoints
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(processing.router, prefix="/api/process", tags=["Processing"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(settings_endpoint.router, prefix="/api/settings", tags=["Settings"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])

# If frontend build exists, mount it and serve index.html for UI
frontend_dist = settings.PROJECT_ROOT / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Allow API and storage routes to pass through
        if full_path.startswith("api") or full_path.startswith("storage") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            from fastapi.responses import FileResponse
            return FileResponse(index_file)
        return {"message": "HoneyBoo API is active."}
else:
    @app.get("/")
    def root():
        return {
            "message": "Welcome to HoneyBoo: Honeybee Entrance Activity & Health Monitoring System API",
            "docs": "/docs",
            "health": "/api/health"
        }

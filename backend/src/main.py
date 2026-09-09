from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    from src.persistence.database import init_db
    await init_db()
    yield
    # Shutdown tasks

app = FastAPI(
    title="Studio Guardian API",
    description="Autonomous Live Media Incident Director",
    version="1.0.0",
    lifespan=lifespan
)

from src.api.incidents import router as incidents_router
from src.api.demo import router as demo_router
from src.api.approvals import router as approvals_router
from src.api.stream import router as stream_router
from src.api.reports import router as reports_router
from src.api.prediction import router as prediction_router
from src.api.provenance import router as provenance_router
from src.api.observability import router as observability_router
from src.api.review import router as review_router

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incidents_router)
app.include_router(demo_router)
app.include_router(approvals_router)
app.include_router(stream_router)
app.include_router(reports_router)
app.include_router(prediction_router)
app.include_router(provenance_router)
app.include_router(observability_router)
app.include_router(review_router)


import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "service": "studio-guardian",
        "version": "1.0.0"
    }

frontend_dist = os.getenv(
    "FRONTEND_DIST",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
)

if os.path.isdir(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return {"name": "Studio Guardian API", "status": "online"}
else:
    @app.get("/")
    async def root():
        return {
            "name": "Studio Guardian API",
            "status": "online",
            "docs_url": "/docs"
        }


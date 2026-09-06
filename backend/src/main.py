from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incidents_router)
app.include_router(demo_router)
app.include_router(approvals_router)
app.include_router(stream_router)
app.include_router(reports_router)

@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "service": "studio-guardian",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "name": "Studio Guardian API",
        "status": "online",
        "docs_url": "/docs"
    }

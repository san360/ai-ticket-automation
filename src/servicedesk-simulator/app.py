"""ServiceDesk Simulator — FastAPI application entry point."""

from fastapi import FastAPI

from routes_api import router as api_router
from routes_ui import router as ui_router

app = FastAPI(
    title="ServiceDesk Simulator",
    version="1.0.0",
    description="Simulated IT Service Desk for AI ticket automation testing. "
    "Provides incident CRUD, attachment download, and feedback endpoints.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router)
app.include_router(ui_router)

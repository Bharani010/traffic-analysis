"""
Traffic Analysis Platform — FastAPI Application Factory.

Production-grade application with structured logging, metrics,
health checks, and clean architecture.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.core.logging import setup_logging
from app.core.metrics import setup_metrics
from app.features.anomalies.router import router as anomalies_router
from app.features.health.router import router as health_router
from app.features.traffic.router import router as traffic_router
from app.middleware.metrics import MetricsMiddleware
from app.middleware.request_id import RequestIdMiddleware

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — startup and shutdown events."""
    setup_logging(log_level=settings.LOG_LEVEL)
    log = structlog.get_logger("lifespan")
    await log.ainfo(
        "Starting Traffic Analysis Platform",
        environment=settings.APP_ENV,
        debug=settings.DEBUG,
    )
    yield
    await log.ainfo("Shutting down Traffic Analysis Platform")
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Traffic Analysis Platform",
        description="AI-Powered Anomaly Detection & Traffic Analysis",
        version="0.1.0",
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware (order matters — outermost first) ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(MetricsMiddleware)

    # ── Metrics endpoint ──
    setup_metrics(app)

    # ── Routers ──
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])
    app.include_router(traffic_router, prefix="/api/v1", tags=["Traffic"])
    app.include_router(anomalies_router, prefix="/api/v1", tags=["Anomalies"])

    return app


app = create_app()

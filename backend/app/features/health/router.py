"""
Health check endpoints.

Provides liveness and readiness probes for container orchestration
and monitoring systems.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.health.service import HealthService

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Liveness probe — confirms the service is running."""
    return HealthService.liveness()


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict:
    """Readiness probe — confirms the service and dependencies are ready."""
    return await HealthService.readiness(db)

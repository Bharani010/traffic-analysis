"""
Health check service.

Encapsulates liveness and readiness logic, including
database connectivity verification.
"""

import time
from datetime import datetime, timezone

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

_start_time = time.monotonic()


class HealthService:
    """Service for application health checks."""

    @staticmethod
    def liveness() -> dict:
        """Simple liveness check — service is running."""
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(time.monotonic() - _start_time, 2),
            "service": "traffic-analysis-backend",
            "version": "0.1.0",
        }

    @staticmethod
    async def readiness(db: AsyncSession) -> dict:
        """Readiness check — service and all dependencies are operational."""
        checks: dict[str, str] = {}

        # Database check
        try:
            await db.execute(text("SELECT 1"))
            checks["database"] = "connected"
        except Exception as exc:
            await logger.awarning("Database readiness check failed", error=str(exc))
            checks["database"] = "disconnected"

        all_healthy = all(v != "disconnected" for v in checks.values())

        return {
            "status": "ready" if all_healthy else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
        }

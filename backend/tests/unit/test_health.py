"""
Unit tests for the health check endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_returns_healthy(client: AsyncClient) -> None:
    """GET /api/v1/health should return status=healthy."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "traffic-analysis-backend"
    assert "uptime_seconds" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_check_returns_version(client: AsyncClient) -> None:
    """Health endpoint should include the application version."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient) -> None:
    """GET /api/v1/health/ready should check dependencies."""
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ready", "degraded")
    assert "checks" in data

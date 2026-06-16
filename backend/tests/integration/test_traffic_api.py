"""
Integration tests for the Traffic API.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_traffic_event(client: AsyncClient) -> None:
    """POST /api/v1/traffic/events should create an event."""
    payload = {
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.1",
        "method": "GET",
        "path": "/api/v1/users",
        "status_code": 200,
        "response_time_ms": 45.2,
        "bytes_sent": 1024,
        "bytes_received": 256,
        "country_code": "US",
    }
    response = await client.post("/api/v1/traffic/events", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["source_ip"] == "192.168.1.100"
    assert data["method"] == "GET"
    assert data["status_code"] == 200
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_traffic_events(client: AsyncClient) -> None:
    """GET /api/v1/traffic/events should return a paginated list."""
    response = await client.get("/api/v1/traffic/events")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


@pytest.mark.asyncio
async def test_create_and_get_event(client: AsyncClient) -> None:
    """Create an event and retrieve it by ID."""
    payload = {
        "source_ip": "10.0.0.50",
        "destination_ip": "10.0.0.1",
        "method": "POST",
        "path": "/api/login",
        "status_code": 401,
        "response_time_ms": 120.5,
        "bytes_sent": 512,
        "bytes_received": 128,
    }
    create_resp = await client.post("/api/v1/traffic/events", json=payload)
    assert create_resp.status_code == 201
    event_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/traffic/events/{event_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["source_ip"] == "10.0.0.50"


@pytest.mark.asyncio
async def test_get_nonexistent_event(client: AsyncClient) -> None:
    """GET with a non-existent ID should return 404."""
    response = await client.get(
        "/api/v1/traffic/events/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404

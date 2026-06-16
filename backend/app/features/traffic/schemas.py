"""
Pydantic schemas for Traffic API request/response validation.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.features.traffic.models import HttpMethod


# ── Request Schemas ──


class TrafficEventCreate(BaseModel):
    """Schema for creating a new traffic event."""

    source_ip: str = Field(..., max_length=45, examples=["192.168.1.100"])
    destination_ip: str = Field(..., max_length=45, examples=["10.0.0.1"])
    method: HttpMethod = Field(..., examples=["GET"])
    path: str = Field(..., max_length=2048, examples=["/api/v1/users"])
    user_agent: str | None = Field(None, examples=["Mozilla/5.0"])
    status_code: int = Field(..., ge=100, le=599, examples=[200])
    response_time_ms: float = Field(..., ge=0, examples=[45.2])
    bytes_sent: int = Field(0, ge=0, examples=[1024])
    bytes_received: int = Field(0, ge=0, examples=[256])
    country_code: str | None = Field(None, max_length=2, examples=["US"])
    session_id: str | None = Field(None, max_length=64)


class TrafficEventFilter(BaseModel):
    """Schema for filtering traffic events."""

    source_ip: str | None = None
    method: HttpMethod | None = None
    status_code: int | None = None
    country_code: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# ── Response Schemas ──


class TrafficEventResponse(BaseModel):
    """Schema for a traffic event response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_ip: str
    destination_ip: str
    method: HttpMethod
    path: str
    user_agent: str | None
    status_code: int
    response_time_ms: float
    bytes_sent: int
    bytes_received: int
    country_code: str | None
    session_id: str | None
    created_at: datetime
    updated_at: datetime


class TrafficEventListResponse(BaseModel):
    """Paginated list of traffic events."""

    items: list[TrafficEventResponse]
    total: int
    limit: int
    offset: int

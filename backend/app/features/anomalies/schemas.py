"""
Pydantic schemas for Anomaly & Incident API.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.features.anomalies.models import (
    AnomalyStatus,
    DetectionMethod,
    IncidentStatus,
    Severity,
)


# ── Anomaly Schemas ──


class AnomalyCreate(BaseModel):
    title: str = Field(..., max_length=256)
    description: str | None = None
    severity: Severity
    detection_method: DetectionMethod
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    source_ip: str | None = None
    affected_endpoint: str | None = None
    event_count: int = Field(1, ge=1)
    raw_details: str | None = None


class AnomalyUpdate(BaseModel):
    status: AnomalyStatus | None = None
    severity: Severity | None = None
    description: str | None = None
    incident_id: uuid.UUID | None = None


class AnomalyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    severity: Severity
    detection_method: DetectionMethod
    status: AnomalyStatus
    confidence_score: float
    source_ip: str | None
    affected_endpoint: str | None
    event_count: int
    incident_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class AnomalyListResponse(BaseModel):
    items: list[AnomalyResponse]
    total: int
    limit: int
    offset: int


# ── Incident Schemas ──


class IncidentCreate(BaseModel):
    title: str = Field(..., max_length=256)
    description: str | None = None
    severity: Severity
    assignee: str | None = None


class IncidentUpdate(BaseModel):
    status: IncidentStatus | None = None
    severity: Severity | None = None
    assignee: str | None = None
    resolution_notes: str | None = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    severity: Severity
    status: IncidentStatus
    assignee: str | None
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime


class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    total: int
    limit: int
    offset: int

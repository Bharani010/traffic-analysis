"""
Anomaly & Incident API router.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.anomalies.models import AnomalyStatus, Severity
from app.features.anomalies.schemas import (
    AnomalyCreate,
    AnomalyListResponse,
    AnomalyResponse,
    AnomalyUpdate,
    IncidentCreate,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdate,
)
from app.features.anomalies.service import AnomalyService

router = APIRouter()


# ── Anomaly Endpoints ──


@router.post(
    "/anomalies",
    response_model=AnomalyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_anomaly(
    data: AnomalyCreate,
    db: AsyncSession = Depends(get_db),
) -> AnomalyResponse:
    """Create a new anomaly."""
    service = AnomalyService(db)
    anomaly = await service.create_anomaly(data)
    return AnomalyResponse.model_validate(anomaly)


@router.get("/anomalies/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(
    anomaly_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AnomalyResponse:
    """Get an anomaly by ID."""
    service = AnomalyService(db)
    anomaly = await service.get_anomaly(str(anomaly_id))
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return AnomalyResponse.model_validate(anomaly)


@router.patch("/anomalies/{anomaly_id}", response_model=AnomalyResponse)
async def update_anomaly(
    anomaly_id: uuid.UUID,
    data: AnomalyUpdate,
    db: AsyncSession = Depends(get_db),
) -> AnomalyResponse:
    """Update an anomaly."""
    service = AnomalyService(db)
    anomaly = await service.update_anomaly(str(anomaly_id), data)
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return AnomalyResponse.model_validate(anomaly)


@router.get("/anomalies", response_model=AnomalyListResponse)
async def list_anomalies(
    severity: Severity | None = Query(None),
    anomaly_status: AnomalyStatus | None = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> AnomalyListResponse:
    """List anomalies with optional filters."""
    service = AnomalyService(db)
    anomalies, total = await service.list_anomalies(
        severity=severity, status=anomaly_status, limit=limit, offset=offset
    )
    return AnomalyListResponse(
        items=[AnomalyResponse.model_validate(a) for a in anomalies],
        total=total,
        limit=limit,
        offset=offset,
    )


# ── Incident Endpoints ──


@router.post(
    "/incidents",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(
    data: IncidentCreate,
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Create a new incident."""
    service = AnomalyService(db)
    incident = await service.create_incident(data)
    return IncidentResponse.model_validate(incident)


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Get an incident by ID."""
    service = AnomalyService(db)
    incident = await service.get_incident(str(incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse.model_validate(incident)


@router.patch("/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: uuid.UUID,
    data: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Update an incident."""
    service = AnomalyService(db)
    incident = await service.update_incident(str(incident_id), data)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse.model_validate(incident)


@router.get("/incidents", response_model=IncidentListResponse)
async def list_incidents(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> IncidentListResponse:
    """List incidents."""
    service = AnomalyService(db)
    incidents, total = await service.list_incidents(limit=limit, offset=offset)
    return IncidentListResponse(
        items=[IncidentResponse.model_validate(i) for i in incidents],
        total=total,
        limit=limit,
        offset=offset,
    )

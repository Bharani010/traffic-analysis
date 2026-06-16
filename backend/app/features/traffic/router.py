"""
Traffic event API router.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.traffic.models import HttpMethod
from app.features.traffic.schemas import (
    TrafficEventCreate,
    TrafficEventFilter,
    TrafficEventListResponse,
    TrafficEventResponse,
)
from app.features.traffic.service import TrafficService

router = APIRouter(prefix="/traffic")


@router.post(
    "/events",
    response_model=TrafficEventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_traffic_event(
    event_data: TrafficEventCreate,
    db: AsyncSession = Depends(get_db),
) -> TrafficEventResponse:
    """Create a new traffic event."""
    service = TrafficService(db)
    event = await service.create_event(event_data)
    return TrafficEventResponse.model_validate(event)


@router.post(
    "/events/bulk",
    status_code=status.HTTP_201_CREATED,
)
async def create_traffic_events_bulk(
    events_data: list[TrafficEventCreate],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Bulk create traffic events."""
    service = TrafficService(db)
    count = await service.create_events_bulk(events_data)
    return {"created": count}


@router.get(
    "/events/{event_id}",
    response_model=TrafficEventResponse,
)
async def get_traffic_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TrafficEventResponse:
    """Get a traffic event by ID."""
    service = TrafficService(db)
    event = await service.get_event(str(event_id))
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Traffic event {event_id} not found",
        )
    return TrafficEventResponse.model_validate(event)


@router.get(
    "/events",
    response_model=TrafficEventListResponse,
)
async def list_traffic_events(
    source_ip: str | None = Query(None),
    method: HttpMethod | None = Query(None),
    status_code: int | None = Query(None, ge=100, le=599),
    country_code: str | None = Query(None, max_length=2),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> TrafficEventListResponse:
    """List traffic events with optional filters and pagination."""
    filters = TrafficEventFilter(
        source_ip=source_ip,
        method=method,
        status_code=status_code,
        country_code=country_code,
        limit=limit,
        offset=offset,
    )
    service = TrafficService(db)
    events, total = await service.list_events(filters)
    return TrafficEventListResponse(
        items=[TrafficEventResponse.model_validate(e) for e in events],
        total=total,
        limit=limit,
        offset=offset,
    )

"""
Traffic event business logic.
"""

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.metrics import EVENTS_PROCESSED
from app.features.traffic.models import TrafficEvent
from app.features.traffic.schemas import TrafficEventCreate, TrafficEventFilter

logger = structlog.get_logger(__name__)


class TrafficService:
    """Service layer for traffic event operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_event(self, event_data: TrafficEventCreate) -> TrafficEvent:
        """Create a new traffic event."""
        event = TrafficEvent(**event_data.model_dump())
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        EVENTS_PROCESSED.inc()
        await logger.ainfo("Traffic event created", event_id=str(event.id))
        return event

    async def create_events_bulk(
        self, events_data: list[TrafficEventCreate]
    ) -> int:
        """Bulk create traffic events. Returns count of created events."""
        events = [TrafficEvent(**e.model_dump()) for e in events_data]
        self.db.add_all(events)
        await self.db.flush()
        count = len(events)
        EVENTS_PROCESSED.inc(count)
        await logger.ainfo("Bulk traffic events created", count=count)
        return count

    async def get_event(self, event_id: str) -> TrafficEvent | None:
        """Get a single traffic event by ID."""
        result = await self.db.execute(
            select(TrafficEvent).where(TrafficEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    async def list_events(
        self, filters: TrafficEventFilter
    ) -> tuple[list[TrafficEvent], int]:
        """List traffic events with filtering and pagination."""
        query = select(TrafficEvent)
        count_query = select(func.count()).select_from(TrafficEvent)

        # Apply filters
        if filters.source_ip:
            query = query.where(TrafficEvent.source_ip == filters.source_ip)
            count_query = count_query.where(TrafficEvent.source_ip == filters.source_ip)
        if filters.method:
            query = query.where(TrafficEvent.method == filters.method)
            count_query = count_query.where(TrafficEvent.method == filters.method)
        if filters.status_code:
            query = query.where(TrafficEvent.status_code == filters.status_code)
            count_query = count_query.where(TrafficEvent.status_code == filters.status_code)
        if filters.country_code:
            query = query.where(TrafficEvent.country_code == filters.country_code)
            count_query = count_query.where(TrafficEvent.country_code == filters.country_code)
        if filters.from_date:
            query = query.where(TrafficEvent.created_at >= filters.from_date)
            count_query = count_query.where(TrafficEvent.created_at >= filters.from_date)
        if filters.to_date:
            query = query.where(TrafficEvent.created_at <= filters.to_date)
            count_query = count_query.where(TrafficEvent.created_at <= filters.to_date)

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = (
            query.order_by(TrafficEvent.created_at.desc())
            .offset(filters.offset)
            .limit(filters.limit)
        )

        result = await self.db.execute(query)
        events = list(result.scalars().all())

        return events, total

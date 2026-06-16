"""
Anomaly detection service layer.
"""

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.metrics import ANOMALIES_DETECTED
from app.features.anomalies.models import Anomaly, AnomalyStatus, Incident, Severity
from app.features.anomalies.schemas import (
    AnomalyCreate,
    AnomalyUpdate,
    IncidentCreate,
    IncidentUpdate,
)

logger = structlog.get_logger(__name__)


class AnomalyService:
    """Service for managing anomalies and incidents."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Anomalies ──

    async def create_anomaly(self, data: AnomalyCreate) -> Anomaly:
        """Create a new anomaly record."""
        anomaly = Anomaly(**data.model_dump())
        self.db.add(anomaly)
        await self.db.flush()
        await self.db.refresh(anomaly)
        ANOMALIES_DETECTED.labels(
            severity=data.severity.value,
            detection_method=data.detection_method.value,
        ).inc()
        await logger.ainfo(
            "Anomaly created",
            anomaly_id=str(anomaly.id),
            severity=data.severity.value,
        )
        return anomaly

    async def get_anomaly(self, anomaly_id: str) -> Anomaly | None:
        result = await self.db.execute(
            select(Anomaly).where(Anomaly.id == anomaly_id)
        )
        return result.scalar_one_or_none()

    async def update_anomaly(
        self, anomaly_id: str, data: AnomalyUpdate
    ) -> Anomaly | None:
        anomaly = await self.get_anomaly(anomaly_id)
        if not anomaly:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(anomaly, field, value)
        await self.db.flush()
        await self.db.refresh(anomaly)
        return anomaly

    async def list_anomalies(
        self,
        severity: Severity | None = None,
        status: AnomalyStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Anomaly], int]:
        query = select(Anomaly)
        count_query = select(func.count()).select_from(Anomaly)

        if severity:
            query = query.where(Anomaly.severity == severity)
            count_query = count_query.where(Anomaly.severity == severity)
        if status:
            query = query.where(Anomaly.status == status)
            count_query = count_query.where(Anomaly.status == status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Anomaly.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    # ── Incidents ──

    async def create_incident(self, data: IncidentCreate) -> Incident:
        incident = Incident(**data.model_dump())
        self.db.add(incident)
        await self.db.flush()
        await self.db.refresh(incident)
        await logger.ainfo("Incident created", incident_id=str(incident.id))
        return incident

    async def get_incident(self, incident_id: str) -> Incident | None:
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        return result.scalar_one_or_none()

    async def update_incident(
        self, incident_id: str, data: IncidentUpdate
    ) -> Incident | None:
        incident = await self.get_incident(incident_id)
        if not incident:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(incident, field, value)
        await self.db.flush()
        await self.db.refresh(incident)
        return incident

    async def list_incidents(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Incident], int]:
        count_result = await self.db.execute(
            select(func.count()).select_from(Incident)
        )
        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(Incident)
            .order_by(Incident.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total

"""
Anomaly, Incident, Rule, and Investigation SQLAlchemy models.
"""

import enum

from sqlalchemy import Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Severity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionMethod(str, enum.Enum):
    RULE_BASED = "rule_based"
    STATISTICAL = "statistical"
    ML_MODEL = "ml_model"
    LLM_AGENT = "llm_agent"


class AnomalyStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class InvestigationStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Rule(Base, UUIDMixin, TimestampMixin):
    """Detection rules."""

    __tablename__ = "rules"

    name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    condition: Mapped[dict] = mapped_column(JSONB, nullable=False)
    action: Mapped[str] = mapped_column(String(256), nullable=False)

    def __repr__(self) -> str:
        return f"<Rule {self.name}>"


class Anomaly(Base, UUIDMixin, TimestampMixin):
    """An anomaly detected in traffic patterns."""

    __tablename__ = "anomalies"

    # ── Detection metadata ──
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity), nullable=False, index=True
    )
    detection_method: Mapped[DetectionMethod] = mapped_column(
        Enum(DetectionMethod), nullable=False
    )
    status: Mapped[AnomalyStatus] = mapped_column(
        Enum(AnomalyStatus), default=AnomalyStatus.OPEN, nullable=False, index=True
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # ── Context ──
    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    affected_endpoint: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    event_count: Mapped[int] = mapped_column(Integer, default=1)
    raw_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ──
    incident_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True
    )
    incident: Mapped["Incident | None"] = relationship(back_populates="anomalies")

    rule_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rules.id", ondelete="SET NULL"), nullable=True
    )
    
    # Optional link to feature entity that triggered this
    feature_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        Index("ix_anomalies_severity_status", "severity", "status"),
        Index("ix_anomalies_detection_method", "detection_method"),
    )

    def __repr__(self) -> str:
        return f"<Anomaly {self.title} severity={self.severity.value} status={self.status.value}>"


class Incident(Base, UUIDMixin, TimestampMixin):
    """An incident aggregating one or more related anomalies."""

    __tablename__ = "incidents"

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity), nullable=False, index=True
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus), default=IncidentStatus.OPEN, nullable=False, index=True
    )
    assignee: Mapped[str | None] = mapped_column(String(128), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ──
    anomalies: Mapped[list["Anomaly"]] = relationship(back_populates="incident")
    investigations: Mapped[list["Investigation"]] = relationship(back_populates="incident")

    def __repr__(self) -> str:
        return f"<Incident {self.title} status={self.status.value}>"


class Investigation(Base, UUIDMixin, TimestampMixin):
    """LLM Agent investigation into an incident."""

    __tablename__ = "investigations"

    incident_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    findings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[InvestigationStatus] = mapped_column(
        Enum(InvestigationStatus), default=InvestigationStatus.PENDING, nullable=False
    )

    # ── Relationships ──
    incident: Mapped["Incident"] = relationship(back_populates="investigations")

    def __repr__(self) -> str:
        return f"<Investigation for incident={self.incident_id} agent={self.agent_id}>"

"""
Traffic event and Feature SQLAlchemy models.
"""

import enum
from datetime import datetime
import uuid

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EntityType(str, enum.Enum):
    IP = "ip"
    SESSION = "session"
    USER = "user"


class RawEvent(Base):
    """Represents a single raw web traffic event.
    Partitioned by timestamp (day) for retention management.
    """

    __tablename__ = "raw_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Timestamp must be part of PK for PostgreSQL partitioning
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True
    )

    # ── Identity ──
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # ── Request ──
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(2048), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(50), nullable=False)

    # ── Response ──
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time: Mapped[float] = mapped_column(Float, nullable=False)

    # ── Sizes ──
    request_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    response_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ── Context ──
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    device: Mapped[str | None] = mapped_column(String(50), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Labels ──
    is_attack: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attack_type: Mapped[str] = mapped_column(String(50), nullable=False, default="normal")

    __table_args__ = (
        Index("ix_raw_events_ip_timestamp", "ip_address", "timestamp"),
        Index("ix_raw_events_session_id", "session_id"),
        Index("ix_raw_events_user_id", "user_id"),
        {"postgresql_partition_by": "RANGE (timestamp)"},
    )

    def __repr__(self) -> str:
        return f"<RawEvent {self.method} {self.endpoint} from={self.ip_address}>"


class Feature(Base):
    """Engineered features aggregated over time windows.
    Partitioned by created_at (day) for retention management.
    """

    __tablename__ = "features"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # created_at must be part of PK for PostgreSQL partitioning
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, default=datetime.utcnow
    )

    entity_type: Mapped[EntityType] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # ── Engineered Features ──
    requests_per_minute: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    failed_login_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_response_time: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    endpoint_entropy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    session_duration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    country_switch_frequency: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unique_user_agents: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        Index("ix_features_entity_time", "entity_type", "entity_id", "created_at"),
        {"postgresql_partition_by": "RANGE (created_at)"},
    )

    def __repr__(self) -> str:
        return f"<Feature {self.entity_type.value}={self.entity_id}>"

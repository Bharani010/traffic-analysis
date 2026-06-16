"""
Traffic event SQLAlchemy models.
"""

import enum

from sqlalchemy import Enum, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class HttpMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class TrafficEvent(Base, UUIDMixin, TimestampMixin):
    """Represents a single web traffic event / HTTP request."""

    __tablename__ = "traffic_events"

    # ── Request metadata ──
    source_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    destination_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    method: Mapped[HttpMethod] = mapped_column(Enum(HttpMethod), nullable=False)
    path: Mapped[str] = mapped_column(String(2048), nullable=False)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Response metadata ──
    status_code: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    bytes_sent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bytes_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ── Geo / context ──
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # ── Indexes for analytics queries ──
    __table_args__ = (
        Index("ix_traffic_events_created_source", "created_at", "source_ip"),
        Index("ix_traffic_events_method_status", "method", "status_code"),
    )

    def __repr__(self) -> str:
        return (
            f"<TrafficEvent {self.method.value} {self.path} "
            f"from={self.source_ip} status={self.status_code}>"
        )

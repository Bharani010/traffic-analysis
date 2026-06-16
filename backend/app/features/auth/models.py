"""
Auth and Identity SQLAlchemy models.
"""

from datetime import datetime
from sqlalchemy import Boolean, Float, ForeignKey, Index, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User profile and identity."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    activity_profile: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ── Relationships ──
    sessions: Mapped[list["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Session(Base, UUIDMixin, TimestampMixin):
    """Browsing session tied to a user."""

    __tablename__ = "sessions"

    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Relationships ──
    user: Mapped["User | None"] = relationship(back_populates="sessions")

    def __repr__(self) -> str:
        return f"<Session user_id={self.user_id} ip={self.ip_address}>"

"""
Traffic event data model.

Defines the canonical event schema used across the entire simulation
engine, data pipeline, and backend.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class TrafficEvent:
    """A single web traffic event with full attribution."""

    # ── Identity ──
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # ── Timing ──
    timestamp: str = ""  # ISO 8601 string for serialization

    # ── Network ──
    ip_address: str = ""
    session_id: str = ""
    user_id: str = ""

    # ── Request ──
    method: str = ""
    endpoint: str = ""
    category: str = ""        # auth, user_activity, api, admin
    subcategory: str = ""     # login, browse, checkout, etc.

    # ── Response ──
    status_code: int = 200
    response_time: float = 0.0   # milliseconds

    # ── Sizes ──
    request_size: int = 0        # bytes
    response_size: int = 0       # bytes

    # ── Context ──
    country: str = ""
    device: str = ""
    browser: str = ""

    # ── Labels ──
    is_attack: bool = False
    attack_type: str = "normal"  # normal | credential_stuffing | brute_force | etc.

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return asdict(self)

    @staticmethod
    def csv_header() -> str:
        """Return CSV header line."""
        return ",".join([
            "event_id", "timestamp", "ip_address", "session_id", "user_id",
            "method", "endpoint", "category", "subcategory",
            "status_code", "response_time", "request_size", "response_size",
            "country", "device", "browser", "is_attack", "attack_type",
        ])

    def to_csv_row(self) -> str:
        """Convert to CSV row."""
        return ",".join([
            self.event_id,
            self.timestamp,
            self.ip_address,
            self.session_id,
            self.user_id,
            self.method,
            self.endpoint,
            self.category,
            self.subcategory,
            str(self.status_code),
            f"{self.response_time:.2f}",
            str(self.request_size),
            str(self.response_size),
            self.country,
            self.device,
            self.browser,
            str(self.is_attack),
            self.attack_type,
        ])

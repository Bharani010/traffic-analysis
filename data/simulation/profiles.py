"""
User, session, and device profile generators.

Creates realistic populations of synthetic users with consistent
behavior patterns, devices, and geographic locations.
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field

from data.simulation import (
    BROWSERS,
    COUNTRIES,
    DEVICES,
    IP_POOLS,
)


@dataclass(slots=True)
class UserProfile:
    """A synthetic user with consistent attributes."""
    user_id: str = ""
    country: str = ""
    primary_device: str = ""
    primary_browser: str = ""
    ip_address: str = ""
    activity_level: float = 1.0    # 0.1 = low, 1.0 = normal, 3.0 = power user
    is_admin: bool = False
    sessions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SessionProfile:
    """A browsing session with a start time and device."""
    session_id: str = ""
    user_id: str = ""
    ip_address: str = ""
    device: str = ""
    browser: str = ""
    country: str = ""
    event_count: int = 0           # How many events in this session


def _pick_weighted(items: list[dict], key: str = "weight") -> dict:
    """Pick an item from a weighted list."""
    weights = [item[key] for item in items]
    return random.choices(items, weights=weights, k=1)[0]


def generate_ip(country_code: str) -> str:
    """Generate a realistic IP address for a given country."""
    templates = IP_POOLS.get(country_code, ["192.168.{}.{}"])
    template = random.choice(templates)
    return template.format(random.randint(1, 254), random.randint(1, 254))


def create_user_population(
    num_users: int = 5000,
    admin_ratio: float = 0.02,
    rng: random.Random | None = None,
) -> list[UserProfile]:
    """
    Create a population of synthetic users.

    Users have:
    - A home country (weighted by real traffic)
    - A primary device and browser
    - An activity level drawn from a log-normal distribution
    - A stable IP address per country

    Args:
        num_users: Number of users to create
        admin_ratio: Fraction of users who are admins
        rng: Optional seeded Random instance

    Returns:
        List of UserProfile instances
    """
    if rng is None:
        rng = random.Random()

    users: list[UserProfile] = []
    num_admins = int(num_users * admin_ratio)

    for i in range(num_users):
        country_data = _pick_weighted(COUNTRIES)
        country = country_data["code"]
        device_data = _pick_weighted(DEVICES)
        device_type = device_data["type"]
        browser_data = _pick_weighted(BROWSERS[device_type])

        # Activity level: log-normal so most users are low activity,
        # a few are power users
        activity = max(0.1, min(5.0, rng.lognormvariate(0, 0.8)))

        user = UserProfile(
            user_id=f"user_{i:06d}",
            country=country,
            primary_device=device_type,
            primary_browser=browser_data["name"],
            ip_address=generate_ip(country),
            activity_level=round(activity, 2),
            is_admin=(i < num_admins),
        )
        users.append(user)

    return users


def create_sessions_for_user(
    user: UserProfile,
    num_sessions: int,
    rng: random.Random | None = None,
) -> list[SessionProfile]:
    """
    Create browsing sessions for a user.

    Most sessions use the user's primary device, but some may switch.
    Each session gets a unique session ID and event count based on
    the user's activity level.

    Args:
        user: The user to create sessions for
        num_sessions: Number of sessions
        rng: Optional seeded Random instance

    Returns:
        List of SessionProfile instances
    """
    if rng is None:
        rng = random.Random()

    sessions: list[SessionProfile] = []

    for _ in range(num_sessions):
        # 80% chance of using primary device, 20% chance of switching
        if rng.random() < 0.80:
            device = user.primary_device
            browser = user.primary_browser
        else:
            device_data = _pick_weighted(DEVICES)
            device = device_data["type"]
            browser_data = _pick_weighted(BROWSERS[device])
            browser = browser_data["name"]

        # Sometimes the user connects from a different IP (VPN, travel)
        if rng.random() < 0.15:
            ip = generate_ip(user.country)
        else:
            ip = user.ip_address

        # Events per session: Poisson-like distribution scaled by activity
        base_events = max(1, int(rng.gauss(12, 6) * user.activity_level))

        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        user.sessions.append(session_id)

        sessions.append(SessionProfile(
            session_id=session_id,
            user_id=user.user_id,
            ip_address=ip,
            device=device,
            browser=browser,
            country=user.country,
            event_count=base_events,
        ))

    return sessions

"""
Event sequence generator and attack injection.

Generates chronological sequences of TrafficEvents for sessions,
including both normal user behavior and injected attack patterns.
"""

import random
from datetime import datetime, timedelta
from typing import Iterator

from data.simulation import (
    ALL_ENDPOINTS,
    ATTACK_LABEL_NORMAL,
    RESPONSE_TIME_PROFILES,
    SIZE_PROFILES,
    STATUS_CODE_DISTRIBUTIONS,
)
from data.simulation.models import TrafficEvent
from data.simulation.profiles import SessionProfile, UserProfile


class EventGenerator:
    """Generates TrafficEvents for given sessions."""

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def _get_response_time(self, category: str) -> float:
        profile = RESPONSE_TIME_PROFILES.get(category, RESPONSE_TIME_PROFILES["user_activity"])
        val = self.rng.gauss(profile["mean"], profile["std"])
        return round(max(profile["min"], min(profile["max"], val)), 2)

    def _get_status_code(self, category: str, is_attack: bool = False, attack_type: str = "") -> int:
        if is_attack:
            if attack_type == "credential_stuffing": return 401
            if attack_type == "brute_force": return 401
            if attack_type == "api_abuse": return 429
            if attack_type == "ddos_burst": return 503
            if attack_type == "injection": return 400
        
        dist = STATUS_CODE_DISTRIBUTIONS.get(category, STATUS_CODE_DISTRIBUTIONS["user_activity"])
        return self.rng.choices(dist["codes"], weights=dist["weights"], k=1)[0]

    def _get_sizes(self, category: str) -> tuple[int, int]:
        profile = SIZE_PROFILES.get(category, SIZE_PROFILES["user_activity"])
        req_size = self.rng.randint(profile["req_min"], profile["req_max"])
        res_size = self.rng.randint(profile["res_min"], profile["res_max"])
        return req_size, res_size

    def generate_normal_session(
        self, session: SessionProfile, start_time: datetime
    ) -> Iterator[TrafficEvent]:
        """Generate a normal sequence of events for a session."""
        current_time = start_time
        endpoints = list(ALL_ENDPOINTS.values())
        
        # Simple markov chain or weighted random flow. For now, random weighted by category might be simpler, 
        # but let's just pick randomly from ALL_ENDPOINTS. In a real engine we'd define specific flows.
        for _ in range(session.event_count):
            endpoint_def = self.rng.choice(endpoints)
            cat = endpoint_def["category"]
            
            req_size, res_size = self._get_sizes(cat)
            
            yield TrafficEvent(
                timestamp=current_time.isoformat(),
                ip_address=session.ip_address,
                session_id=session.session_id,
                user_id=session.user_id,
                method=endpoint_def["method"],
                endpoint=endpoint_def["path"],
                category=cat,
                subcategory=endpoint_def["subcategory"],
                status_code=self._get_status_code(cat),
                response_time=self._get_response_time(cat),
                request_size=req_size,
                response_size=res_size,
                country=session.country,
                device=session.device,
                browser=session.browser,
                is_attack=False,
                attack_type=ATTACK_LABEL_NORMAL
            )
            
            # Advance time by a few seconds between requests
            current_time += timedelta(seconds=self.rng.expovariate(1.0 / 15.0) + 1)

    # ── Attack Injectors ──

    def inject_credential_stuffing(
        self, start_time: datetime, count: int, endpoints: list[dict]
    ) -> Iterator[TrafficEvent]:
        """Distributed IPs targeting login."""
        current_time = start_time
        login_ep = ALL_ENDPOINTS["POST /api/v1/auth/login"]
        
        for _ in range(count):
            # Randomize IP for each attempt
            ip = f"{self.rng.randint(1,254)}.{self.rng.randint(1,254)}.{self.rng.randint(1,254)}.{self.rng.randint(1,254)}"
            req_size, res_size = self._get_sizes(login_ep["category"])
            yield TrafficEvent(
                timestamp=current_time.isoformat(),
                ip_address=ip,
                session_id=f"sess_stuff_{self.rng.randint(1000,9999)}",
                user_id="",
                method=login_ep["method"],
                endpoint=login_ep["path"],
                category=login_ep["category"],
                subcategory=login_ep["subcategory"],
                status_code=401, # Mostly fail
                response_time=self._get_response_time(login_ep["category"]),
                request_size=req_size,
                response_size=res_size,
                country="Unknown",
                device="bot",
                browser="python-requests/2.31.0",
                is_attack=True,
                attack_type="credential_stuffing"
            )
            current_time += timedelta(milliseconds=self.rng.randint(100, 500))

    def inject_brute_force(
        self, user: UserProfile, start_time: datetime, count: int
    ) -> Iterator[TrafficEvent]:
        """Single IP rapid-fire on login."""
        current_time = start_time
        login_ep = ALL_ENDPOINTS["POST /api/v1/auth/login"]
        attacker_ip = "185.15.2.44" # Example malicious IP
        
        for _ in range(count):
            req_size, res_size = self._get_sizes(login_ep["category"])
            yield TrafficEvent(
                timestamp=current_time.isoformat(),
                ip_address=attacker_ip,
                session_id=f"sess_brute_{user.user_id}",
                user_id=user.user_id,
                method=login_ep["method"],
                endpoint=login_ep["path"],
                category=login_ep["category"],
                subcategory=login_ep["subcategory"],
                status_code=401, 
                response_time=self._get_response_time(login_ep["category"]),
                request_size=req_size,
                response_size=res_size,
                country="RU",
                device="desktop",
                browser="curl/8.4.0",
                is_attack=True,
                attack_type="brute_force"
            )
            current_time += timedelta(milliseconds=self.rng.randint(50, 200))

    def inject_ddos_burst(
        self, start_time: datetime, count: int
    ) -> Iterator[TrafficEvent]:
        """Massive volume of requests from multiple IPs."""
        current_time = start_time
        endpoints = list(ALL_ENDPOINTS.values())
        
        for _ in range(count):
            ip = f"{self.rng.randint(1,254)}.{self.rng.randint(1,254)}.{self.rng.randint(1,254)}.{self.rng.randint(1,254)}"
            ep = self.rng.choice(endpoints)
            req_size, res_size = self._get_sizes(ep["category"])
            yield TrafficEvent(
                timestamp=current_time.isoformat(),
                ip_address=ip,
                session_id="",
                user_id="",
                method=ep["method"],
                endpoint=ep["path"],
                category=ep["category"],
                subcategory=ep["subcategory"],
                status_code=503, # Overloaded
                response_time=self.rng.uniform(2000, 5000), # Very slow
                request_size=req_size,
                response_size=res_size,
                country="Unknown",
                device="bot",
                browser="Unknown",
                is_attack=True,
                attack_type="ddos_burst"
            )
            current_time += timedelta(milliseconds=self.rng.randint(1, 10))

    def inject_api_abuse(
        self, user: UserProfile, start_time: datetime, count: int
    ) -> Iterator[TrafficEvent]:
        """High frequency calls to data endpoints."""
        current_time = start_time
        search_ep = ALL_ENDPOINTS["GET /api/v1/search"]
        
        for _ in range(count):
            req_size, res_size = self._get_sizes(search_ep["category"])
            yield TrafficEvent(
                timestamp=current_time.isoformat(),
                ip_address=user.ip_address,
                session_id=f"sess_abuse_{user.user_id}",
                user_id=user.user_id,
                method=search_ep["method"],
                endpoint=search_ep["path"],
                category=search_ep["category"],
                subcategory=search_ep["subcategory"],
                status_code=429, # Rate limited
                response_time=self._get_response_time(search_ep["category"]),
                request_size=req_size,
                response_size=res_size,
                country=user.country,
                device="api_client",
                browser="python-httpx/0.27.0",
                is_attack=True,
                attack_type="api_abuse"
            )
            current_time += timedelta(milliseconds=self.rng.randint(20, 100))

    def inject_bot_crawling(
        self, start_time: datetime, count: int
    ) -> Iterator[TrafficEvent]:
        """Sequential fast accesses without static assets."""
        current_time = start_time
        browse_eps = [v for k,v in ALL_ENDPOINTS.items() if v["subcategory"] == "browse"]
        ip = f"{self.rng.randint(1,254)}.{self.rng.randint(1,254)}.{self.rng.randint(1,254)}.{self.rng.randint(1,254)}"
        
        for _ in range(count):
            ep = self.rng.choice(browse_eps)
            req_size, res_size = self._get_sizes(ep["category"])
            yield TrafficEvent(
                timestamp=current_time.isoformat(),
                ip_address=ip,
                session_id="",
                user_id="",
                method=ep["method"],
                endpoint=ep["path"],
                category=ep["category"],
                subcategory=ep["subcategory"],
                status_code=200, 
                response_time=self._get_response_time(ep["category"]),
                request_size=req_size,
                response_size=res_size,
                country="Unknown",
                device="bot",
                browser="Googlebot/2.1",
                is_attack=True,
                attack_type="bot_crawling"
            )
            current_time += timedelta(milliseconds=self.rng.randint(500, 1500))

    def inject_geo_takeover(
        self, user: UserProfile, start_time: datetime, count: int
    ) -> Iterator[TrafficEvent]:
        """Login attempts from anomalous countries."""
        current_time = start_time
        login_ep = ALL_ENDPOINTS["POST /api/v1/auth/login"]
        attacker_ip = "41.203.2.1" # Example IP from a different country
        
        for _ in range(count):
            req_size, res_size = self._get_sizes(login_ep["category"])
            yield TrafficEvent(
                timestamp=current_time.isoformat(),
                ip_address=attacker_ip,
                session_id=f"sess_geo_{user.user_id}",
                user_id=user.user_id,
                method=login_ep["method"],
                endpoint=login_ep["path"],
                category=login_ep["category"],
                subcategory=login_ep["subcategory"],
                status_code=self.rng.choice([200, 401]), 
                response_time=self._get_response_time(login_ep["category"]),
                request_size=req_size,
                response_size=res_size,
                country="NG", # Different from user's usual country
                device="mobile",
                browser="Chrome Mobile/125.0",
                is_attack=True,
                attack_type="geo_account_takeover"
            )
            current_time += timedelta(seconds=self.rng.randint(10, 60))

    def inject_session_hijacking(
        self, session: SessionProfile, start_time: datetime, count: int
    ) -> Iterator[TrafficEvent]:
        """Session ID reuse from entirely different IPs/devices."""
        current_time = start_time
        endpoints = [v for k,v in ALL_ENDPOINTS.items() if v["category"] == "user_activity"]
        attacker_ip = "185.15.2.44"
        
        for _ in range(count):
            ep = self.rng.choice(endpoints)
            req_size, res_size = self._get_sizes(ep["category"])
            yield TrafficEvent(
                timestamp=current_time.isoformat(),
                ip_address=attacker_ip, # Different IP
                session_id=session.session_id, # Stolen session ID
                user_id=session.user_id,
                method=ep["method"],
                endpoint=ep["path"],
                category=ep["category"],
                subcategory=ep["subcategory"],
                status_code=200, 
                response_time=self._get_response_time(ep["category"]),
                request_size=req_size,
                response_size=res_size,
                country="RU",
                device="desktop", # Different device possibly
                browser="Firefox/126.0",
                is_attack=True,
                attack_type="session_hijacking"
            )
            current_time += timedelta(seconds=self.rng.randint(2, 10))

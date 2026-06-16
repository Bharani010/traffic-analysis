"""
Simulation engine configuration.

All constants, distributions, endpoint definitions, and profile data
used by the traffic simulation engine.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

# ══════════════════════════════════════════════════════════════════════════════
# Endpoint Definitions — organized by category
# ══════════════════════════════════════════════════════════════════════════════

AUTH_ENDPOINTS = {
    "POST /api/v1/auth/login": {"method": "POST", "path": "/api/v1/auth/login", "category": "auth", "subcategory": "login"},
    "POST /api/v1/auth/logout": {"method": "POST", "path": "/api/v1/auth/logout", "category": "auth", "subcategory": "logout"},
    "POST /api/v1/auth/register": {"method": "POST", "path": "/api/v1/auth/register", "category": "auth", "subcategory": "register"},
    "POST /api/v1/auth/password-reset": {"method": "POST", "path": "/api/v1/auth/password-reset", "category": "auth", "subcategory": "password_reset"},
    "POST /api/v1/auth/password-reset/confirm": {"method": "POST", "path": "/api/v1/auth/password-reset/confirm", "category": "auth", "subcategory": "password_reset"},
    "POST /api/v1/auth/refresh": {"method": "POST", "path": "/api/v1/auth/refresh", "category": "auth", "subcategory": "login"},
    "GET /api/v1/auth/me": {"method": "GET", "path": "/api/v1/auth/me", "category": "auth", "subcategory": "login"},
}

USER_ACTIVITY_ENDPOINTS = {
    "GET /api/v1/search": {"method": "GET", "path": "/api/v1/search", "category": "user_activity", "subcategory": "search"},
    "GET /api/v1/products": {"method": "GET", "path": "/api/v1/products", "category": "user_activity", "subcategory": "browse"},
    "GET /api/v1/products/{id}": {"method": "GET", "path": "/api/v1/products/{id}", "category": "user_activity", "subcategory": "browse"},
    "GET /api/v1/categories": {"method": "GET", "path": "/api/v1/categories", "category": "user_activity", "subcategory": "browse"},
    "GET /api/v1/categories/{id}": {"method": "GET", "path": "/api/v1/categories/{id}", "category": "user_activity", "subcategory": "browse"},
    "POST /api/v1/cart/items": {"method": "POST", "path": "/api/v1/cart/items", "category": "user_activity", "subcategory": "checkout"},
    "GET /api/v1/cart": {"method": "GET", "path": "/api/v1/cart", "category": "user_activity", "subcategory": "checkout"},
    "DELETE /api/v1/cart/items/{id}": {"method": "DELETE", "path": "/api/v1/cart/items/{id}", "category": "user_activity", "subcategory": "checkout"},
    "POST /api/v1/orders": {"method": "POST", "path": "/api/v1/orders", "category": "user_activity", "subcategory": "checkout"},
    "GET /api/v1/orders": {"method": "GET", "path": "/api/v1/orders", "category": "user_activity", "subcategory": "checkout"},
    "GET /api/v1/orders/{id}": {"method": "GET", "path": "/api/v1/orders/{id}", "category": "user_activity", "subcategory": "checkout"},
    "GET /api/v1/profile": {"method": "GET", "path": "/api/v1/profile", "category": "user_activity", "subcategory": "browse"},
    "PATCH /api/v1/profile": {"method": "PATCH", "path": "/api/v1/profile", "category": "user_activity", "subcategory": "browse"},
    "GET /api/v1/wishlist": {"method": "GET", "path": "/api/v1/wishlist", "category": "user_activity", "subcategory": "browse"},
    "POST /api/v1/wishlist": {"method": "POST", "path": "/api/v1/wishlist", "category": "user_activity", "subcategory": "browse"},
    "GET /api/v1/reviews": {"method": "GET", "path": "/api/v1/reviews", "category": "user_activity", "subcategory": "browse"},
    "POST /api/v1/reviews": {"method": "POST", "path": "/api/v1/reviews", "category": "user_activity", "subcategory": "browse"},
}

API_CALL_ENDPOINTS = {
    "GET /api/v1/health": {"method": "GET", "path": "/api/v1/health", "category": "api", "subcategory": "health"},
    "GET /api/v1/status": {"method": "GET", "path": "/api/v1/status", "category": "api", "subcategory": "health"},
    "GET /api/v1/metrics": {"method": "GET", "path": "/api/v1/metrics", "category": "api", "subcategory": "monitoring"},
    "POST /api/v1/webhooks": {"method": "POST", "path": "/api/v1/webhooks", "category": "api", "subcategory": "integration"},
    "GET /api/v1/webhooks": {"method": "GET", "path": "/api/v1/webhooks", "category": "api", "subcategory": "integration"},
    "PATCH /api/v1/webhooks/{id}": {"method": "PATCH", "path": "/api/v1/webhooks/{id}", "category": "api", "subcategory": "integration"},
    "DELETE /api/v1/webhooks/{id}": {"method": "DELETE", "path": "/api/v1/webhooks/{id}", "category": "api", "subcategory": "integration"},
    "GET /api/v1/analytics/traffic": {"method": "GET", "path": "/api/v1/analytics/traffic", "category": "api", "subcategory": "analytics"},
    "GET /api/v1/analytics/conversions": {"method": "GET", "path": "/api/v1/analytics/conversions", "category": "api", "subcategory": "analytics"},
    "POST /api/v1/notifications": {"method": "POST", "path": "/api/v1/notifications", "category": "api", "subcategory": "integration"},
}

ADMIN_ENDPOINTS = {
    "GET /admin/dashboard": {"method": "GET", "path": "/admin/dashboard", "category": "admin", "subcategory": "dashboard"},
    "GET /admin/analytics": {"method": "GET", "path": "/admin/analytics", "category": "admin", "subcategory": "dashboard"},
    "GET /admin/users": {"method": "GET", "path": "/admin/users", "category": "admin", "subcategory": "user_management"},
    "GET /admin/users/{id}": {"method": "GET", "path": "/admin/users/{id}", "category": "admin", "subcategory": "user_management"},
    "PATCH /admin/users/{id}": {"method": "PATCH", "path": "/admin/users/{id}", "category": "admin", "subcategory": "user_management"},
    "DELETE /admin/users/{id}": {"method": "DELETE", "path": "/admin/users/{id}", "category": "admin", "subcategory": "user_management"},
    "POST /admin/users/{id}/ban": {"method": "POST", "path": "/admin/users/{id}/ban", "category": "admin", "subcategory": "user_management"},
    "GET /admin/settings": {"method": "GET", "path": "/admin/settings", "category": "admin", "subcategory": "dashboard"},
    "PATCH /admin/settings": {"method": "PATCH", "path": "/admin/settings", "category": "admin", "subcategory": "dashboard"},
    "GET /admin/logs": {"method": "GET", "path": "/admin/logs", "category": "admin", "subcategory": "dashboard"},
    "GET /admin/reports": {"method": "GET", "path": "/admin/reports", "category": "admin", "subcategory": "dashboard"},
}

ALL_ENDPOINTS = {
    **AUTH_ENDPOINTS,
    **USER_ACTIVITY_ENDPOINTS,
    **API_CALL_ENDPOINTS,
    **ADMIN_ENDPOINTS,
}

# ── Traffic category weights (how traffic is distributed) ──
CATEGORY_WEIGHTS = {
    "auth": 0.12,            # 12% authentication traffic
    "user_activity": 0.58,   # 58% user browsing/shopping
    "api": 0.20,             # 20% API/integration calls
    "admin": 0.10,           # 10% admin activity
}

# ══════════════════════════════════════════════════════════════════════════════
# User & Device Profiles
# ══════════════════════════════════════════════════════════════════════════════

DEVICES = [
    {"type": "desktop", "weight": 0.45},
    {"type": "mobile", "weight": 0.40},
    {"type": "tablet", "weight": 0.10},
    {"type": "bot", "weight": 0.03},
    {"type": "api_client", "weight": 0.02},
]

BROWSERS = {
    "desktop": [
        {"name": "Chrome/125.0.6422.113", "weight": 0.55},
        {"name": "Firefox/126.0", "weight": 0.15},
        {"name": "Safari/17.5", "weight": 0.15},
        {"name": "Edge/125.0.2535.79", "weight": 0.12},
        {"name": "Opera/111.0.5168.43", "weight": 0.03},
    ],
    "mobile": [
        {"name": "Chrome Mobile/125.0.6422.113", "weight": 0.45},
        {"name": "Safari Mobile/17.5", "weight": 0.35},
        {"name": "Samsung Internet/25.0", "weight": 0.10},
        {"name": "Firefox Mobile/126.0", "weight": 0.05},
        {"name": "Opera Mobile/82.0", "weight": 0.05},
    ],
    "tablet": [
        {"name": "Safari/17.5", "weight": 0.50},
        {"name": "Chrome/125.0.6422.113", "weight": 0.40},
        {"name": "Firefox/126.0", "weight": 0.10},
    ],
    "bot": [
        {"name": "Googlebot/2.1", "weight": 0.30},
        {"name": "Bingbot/2.0", "weight": 0.20},
        {"name": "python-requests/2.31.0", "weight": 0.20},
        {"name": "curl/8.7.1", "weight": 0.15},
        {"name": "scrapy/2.11", "weight": 0.15},
    ],
    "api_client": [
        {"name": "PostmanRuntime/7.37.0", "weight": 0.30},
        {"name": "axios/1.7.0", "weight": 0.25},
        {"name": "python-httpx/0.27.0", "weight": 0.20},
        {"name": "Go-http-client/2.0", "weight": 0.15},
        {"name": "java/21.0.3", "weight": 0.10},
    ],
}

# ── Geographic distribution (weighted by real-world traffic patterns) ──
COUNTRIES = [
    {"code": "US", "weight": 0.30, "tz_offset": -5},
    {"code": "GB", "weight": 0.08, "tz_offset": 0},
    {"code": "DE", "weight": 0.07, "tz_offset": 1},
    {"code": "FR", "weight": 0.05, "tz_offset": 1},
    {"code": "JP", "weight": 0.06, "tz_offset": 9},
    {"code": "CN", "weight": 0.08, "tz_offset": 8},
    {"code": "IN", "weight": 0.09, "tz_offset": 5},
    {"code": "BR", "weight": 0.06, "tz_offset": -3},
    {"code": "AU", "weight": 0.04, "tz_offset": 10},
    {"code": "CA", "weight": 0.05, "tz_offset": -5},
    {"code": "KR", "weight": 0.03, "tz_offset": 9},
    {"code": "MX", "weight": 0.03, "tz_offset": -6},
    {"code": "RU", "weight": 0.02, "tz_offset": 3},
    {"code": "NG", "weight": 0.02, "tz_offset": 1},
    {"code": "SE", "weight": 0.02, "tz_offset": 1},
]

# ── IP subnet pools per country ──
IP_POOLS = {
    "US": ["44.192.{}.{}", "3.236.{}.{}", "52.7.{}.{}", "100.24.{}.{}"],
    "GB": ["18.130.{}.{}", "35.178.{}.{}", "3.11.{}.{}"],
    "DE": ["3.120.{}.{}", "18.185.{}.{}", "52.59.{}.{}"],
    "FR": ["15.237.{}.{}", "35.180.{}.{}"],
    "JP": ["13.231.{}.{}", "52.69.{}.{}", "3.115.{}.{}"],
    "CN": ["47.94.{}.{}", "120.77.{}.{}", "39.96.{}.{}"],
    "IN": ["13.235.{}.{}", "3.7.{}.{}"],
    "BR": ["15.229.{}.{}", "54.233.{}.{}"],
    "AU": ["13.238.{}.{}", "52.65.{}.{}"],
    "CA": ["3.97.{}.{}", "35.183.{}.{}"],
    "KR": ["3.38.{}.{}", "13.125.{}.{}"],
    "MX": ["44.215.{}.{}"],
    "RU": ["178.154.{}.{}", "89.169.{}.{}"],
    "NG": ["41.190.{}.{}"],
    "SE": ["13.48.{}.{}"],
}

# ── Response time distributions (ms) by endpoint category ──
RESPONSE_TIME_PROFILES = {
    "auth": {"mean": 150, "std": 50, "min": 30, "max": 800},
    "user_activity": {"mean": 120, "std": 60, "min": 20, "max": 2000},
    "api": {"mean": 80, "std": 30, "min": 10, "max": 500},
    "admin": {"mean": 200, "std": 80, "min": 50, "max": 3000},
}

# ── Status code distributions by category ──
STATUS_CODE_DISTRIBUTIONS = {
    "auth": {
        "codes": [200, 201, 400, 401, 403, 422, 429, 500],
        "weights": [50, 10, 10, 15, 5, 5, 3, 2],
    },
    "user_activity": {
        "codes": [200, 201, 301, 304, 400, 404, 500],
        "weights": [65, 8, 5, 10, 4, 6, 2],
    },
    "api": {
        "codes": [200, 201, 204, 400, 401, 403, 404, 429, 500, 503],
        "weights": [55, 10, 5, 6, 4, 3, 7, 4, 4, 2],
    },
    "admin": {
        "codes": [200, 201, 204, 400, 403, 404, 500],
        "weights": [60, 8, 5, 8, 10, 5, 4],
    },
}

# ── Request/response size ranges (bytes) ──
SIZE_PROFILES = {
    "auth": {"req_min": 100, "req_max": 2000, "res_min": 200, "res_max": 5000},
    "user_activity": {"req_min": 50, "req_max": 5000, "res_min": 500, "res_max": 100000},
    "api": {"req_min": 100, "req_max": 10000, "res_min": 200, "res_max": 50000},
    "admin": {"req_min": 100, "req_max": 3000, "res_min": 1000, "res_max": 200000},
}


# ══════════════════════════════════════════════════════════════════════════════
# Attack Configuration (Phase 3)
# ══════════════════════════════════════════════════════════════════════════════

ATTACK_LABEL_NORMAL = "normal"

ATTACK_TYPES = {
    "credential_stuffing": {
        "label": "credential_stuffing",
        "ratio": 0.012,     # 1.2% of total events
        "description": "Automated login attempts with stolen credential lists",
    },
    "brute_force": {
        "label": "brute_force",
        "ratio": 0.008,     # 0.8%
        "description": "Repeated password guessing against single accounts",
    },
    "bot_crawling": {
        "label": "bot_crawling",
        "ratio": 0.010,     # 1.0%
        "description": "Automated scraping/crawling across site endpoints",
    },
    "api_abuse": {
        "label": "api_abuse",
        "ratio": 0.006,     # 0.6%
        "description": "API rate limit violations and data scraping via API",
    },
    "ddos_burst": {
        "label": "ddos_burst",
        "ratio": 0.005,     # 0.5%
        "description": "Distributed denial-of-service flood bursts",
    },
    "geo_account_takeover": {
        "label": "geo_account_takeover",
        "ratio": 0.004,     # 0.4%
        "description": "Login from impossible geographic distance in short time",
    },
    "session_hijacking": {
        "label": "session_hijacking",
        "ratio": 0.005,     # 0.5%
        "description": "Session token reuse from different IPs/devices",
    },
}

# Total attack ratio ≈ 5%
TOTAL_ATTACK_RATIO = sum(a["ratio"] for a in ATTACK_TYPES.values())
NORMAL_RATIO = 1.0 - TOTAL_ATTACK_RATIO


# ══════════════════════════════════════════════════════════════════════════════
# Simulation Config Dataclass
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""
    total_events: int = 1_000_000
    num_users: int = 5000
    num_sessions_per_user: int = 8
    time_span_days: int = 30
    seed: int = 42
    output_format: str = "parquet"   # parquet, csv, json
    output_path: str = "data/output"
    batch_size: int = 50_000         # For memory-efficient generation

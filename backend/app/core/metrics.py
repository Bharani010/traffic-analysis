"""
Prometheus metrics setup.

Exposes a /metrics endpoint for Prometheus scraping and provides
pre-defined counters, histograms, and gauges.
"""

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from fastapi import FastAPI, Response

# ── Pre-defined metrics ──

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Number of active HTTP requests",
)

ANOMALIES_DETECTED = Counter(
    "anomalies_detected_total",
    "Total number of anomalies detected",
    ["severity", "detection_method"],
)

EVENTS_PROCESSED = Counter(
    "traffic_events_processed_total",
    "Total number of traffic events processed",
)


def setup_metrics(app: FastAPI) -> None:
    """Register the /metrics endpoint for Prometheus scraping."""

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> Response:
        return Response(
            content=generate_latest(),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

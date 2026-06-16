"""
Metrics middleware.

Records request count, duration, and active request gauge
for Prometheus monitoring.
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import ACTIVE_REQUESTS, REQUEST_COUNT, REQUEST_DURATION


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that records HTTP metrics for Prometheus."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip metrics for the metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        path = request.url.path

        ACTIVE_REQUESTS.inc()
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            status_code = str(response.status_code)
        except Exception:
            status_code = "500"
            raise
        finally:
            duration = time.perf_counter() - start_time
            ACTIVE_REQUESTS.dec()
            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=status_code,
            ).inc()
            REQUEST_DURATION.labels(
                method=method,
                endpoint=path,
            ).observe(duration)

        return response

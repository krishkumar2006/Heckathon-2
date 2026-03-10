"""Request logging and metrics middleware for observability."""

import time
import logging
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("todo.requests")

# Simple in-memory metrics counters
_metrics = {
    "requests_total": 0,
    "requests_by_method": defaultdict(int),
    "requests_by_status": defaultdict(int),
    "requests_by_path": defaultdict(int),
    "total_response_time_ms": 0.0,
    "errors_total": 0,
}


def get_metrics() -> dict:
    """Return current metrics snapshot."""
    avg_response = 0.0
    if _metrics["requests_total"] > 0:
        avg_response = _metrics["total_response_time_ms"] / _metrics["requests_total"]
    return {
        "requests_total": _metrics["requests_total"],
        "requests_by_method": dict(_metrics["requests_by_method"]),
        "requests_by_status": dict(_metrics["requests_by_status"]),
        "requests_by_path": dict(_metrics["requests_by_path"]),
        "avg_response_time_ms": round(avg_response, 2),
        "errors_total": _metrics["errors_total"],
    }


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every request with method, path, status, and duration."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        path = request.url.path
        method = request.method

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start) * 1000
            status = response.status_code

            # Update metrics
            _metrics["requests_total"] += 1
            _metrics["requests_by_method"][method] += 1
            _metrics["requests_by_status"][str(status)] += 1
            _metrics["requests_by_path"][path] += 1
            _metrics["total_response_time_ms"] += duration_ms
            if status >= 500:
                _metrics["errors_total"] += 1

            # Log request (skip health checks to reduce noise)
            if path not in ("/health", "/ready"):
                logger.info(
                    "%s %s %d %.1fms",
                    method,
                    path,
                    status,
                    duration_ms,
                )

            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            _metrics["requests_total"] += 1
            _metrics["errors_total"] += 1
            logger.error(
                "%s %s ERROR %.1fms %s",
                method,
                path,
                duration_ms,
                str(exc),
            )
            raise

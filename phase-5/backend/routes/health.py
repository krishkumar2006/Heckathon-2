"""Health, readiness, and metrics endpoints."""

import os
import logging

import httpx
from fastapi import APIRouter

from db import get_engine
from middleware.logging_middleware import get_metrics

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")


@router.get("/health")
def health_check():
    """Liveness probe -- returns 200 if service is alive."""
    return {"status": "healthy", "version": "phase-5"}


@router.get("/ready")
async def readiness_check():
    """Readiness probe -- checks DB connection and Dapr sidecar."""
    checks = {"database": False, "dapr": False}

    # Check database connection
    try:
        engine = get_engine()
        from sqlmodel import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.warning("Database readiness check failed: %s", str(e))

    # Check Dapr sidecar
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/healthz",
                timeout=2.0,
            )
            checks["dapr"] = resp.status_code == 204 or resp.status_code == 200
    except Exception:
        logger.warning("Dapr sidecar not reachable")

    # Dapr is optional — only DB is required for readiness
    is_ready = checks["database"]
    status_code = 200 if is_ready else 503
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if is_ready else "not_ready", "checks": checks},
    )


@router.get("/metrics")
def metrics():
    """Application metrics endpoint for monitoring."""
    return get_metrics()

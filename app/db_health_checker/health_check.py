"""
DB health check: verifies database is reachable using the shared connection pool.
Fast: reuses the provider's pooled engine (no new engine per request).
Requires DB provider to be initialized at app startup (main.py lifespan).
"""

import logging
from typing import Any

from fastapi import APIRouter, status

from app.config.database_session_provider import get_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


def check_db_available() -> dict[str, Any]:
    """
    Ping primary (and replica if configured) using the shared pool. One SELECT 1 per engine.
    Returns a dict suitable for JSON response.
    """
    try:
        raw = get_provider().health_check()
        primary_ok = raw.get("primary", False)
        return {
            "status": "online" if primary_ok else "offline",
            "database": "available" if primary_ok else "unavailable",
            "primary": primary_ok,
            "replica": raw.get("replica"),
            "replica_fallback_active": raw.get("replica_fallback_active"),
        }
    except Exception as exc:
        logger.exception("DB health check failed: %s", exc)
        return {
            "status": "offline",
            "database": "unavailable",
            "primary": False,
            "replica": None,
            "replica_fallback_active": False,
        }


@router.get("", status_code=status.HTTP_200_OK)
def health_route() -> dict[str, Any]:
    """
    GET /health — Check DB is available (uses pooled connection, fast).
    """
    return check_db_available()

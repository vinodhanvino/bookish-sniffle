"""
DB health check: verifies database is reachable and returns status for a route.
Uses app.settings (via _config) and database_engine.ping_engine.
"""

import logging
from typing import Any

from fastapi import APIRouter, status

from app.config._config import PRIMARY_CONFIG
from app.config.database_engine import build_engine, ping_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


def check_db_available() -> dict[str, Any]:
    """
    Ping the primary DB (from settings). Does not require provider to be initialized.
    Returns a dict suitable for JSON response.
    """
    engine = None
    try:
        engine = build_engine(PRIMARY_CONFIG, label="health")
        primary_ok = ping_engine(engine, "primary")
    except Exception as exc:
        logger.exception("DB health check failed: %s", exc)
        primary_ok = False
    finally:
        if engine is not None:
            engine.dispose()

    return {
        "status": "online" if primary_ok else "offline",
        "database": "available" if primary_ok else "unavailable",
        "primary": primary_ok,
    }


@router.get("", status_code=status.HTTP_200_OK)
def health_route() -> dict[str, Any]:
    """
    GET /health — Check DB is available and connectable.
    Returns 200 with status "online" when DB is reachable.
    """
    return check_db_available()

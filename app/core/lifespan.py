"""FastAPI lifespan: initialize DB pool at startup, dispose on shutdown."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config._config import PRIMARY_CONFIG, REPLICA_CONFIG, REPLICA_FALLBACK
from app.config.database_session_provider import get_provider

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(_app: FastAPI) -> AsyncIterator[None]:
    try:
        get_provider(
            primary_config=PRIMARY_CONFIG,
            replica_config=REPLICA_CONFIG,
            replica_fallback=REPLICA_FALLBACK,
        )
        logger.info("DB provider initialized (connection pool ready)")
    except Exception as exc:
        logger.exception("DB provider startup failed: %s", exc)
        raise
    yield
    try:
        get_provider().dispose_all()
        logger.info("DB provider disposed")
    except Exception as exc:
        logger.exception("DB provider shutdown error: %s", exc)

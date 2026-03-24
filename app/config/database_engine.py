# =============================================================================
# engine_factory.py  —  Builds SQLAlchemy Engine objects from DBConfig.
# One function, one responsibility.
# =============================================================================

import logging

from sqlalchemy import create_engine, Engine, text

from app.config._config import DBConfig

logger = logging.getLogger(__name__)


def build_engine(cfg: DBConfig, label: str = "db") -> Engine:
    """
    Create a SQLAlchemy Engine with a QueuePool configured from DBConfig.

    Args:
        cfg:    DBConfig instance (primary or replica).
        label:  Human-readable name used only for log messages.

    Returns:
        A connected, pooled SQLAlchemy Engine.

    Raises:
        sqlalchemy.exc.OperationalError  if the database is unreachable.
    """
    engine = create_engine(
        cfg.url,
        pool_size=cfg.pool_size,
        max_overflow=cfg.max_overflow,
        pool_timeout=cfg.pool_timeout,
        pool_recycle=cfg.pool_recycle,
        pool_pre_ping=cfg.pool_pre_ping,
        **cfg.engine_kwargs,
    )

    logger.info(
        "Engine created [%s]  host=%s  db=%s  pool_size=%d  max_overflow=%d",
        label, cfg.host, cfg.database, cfg.pool_size, cfg.max_overflow,
    )
    return engine


def ping_engine(engine: Engine, label: str = "db") -> bool:
    """
    Execute a lightweight SELECT 1 to verify the engine can reach the database.

    Returns:
        True  if reachable.
        False if unreachable (logs the error, does NOT raise).
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.debug("Ping OK [%s]", label)
        return True
    except Exception as exc:
        logger.error("Ping FAILED [%s]: %s", label, exc)
        return False

# =============================================================================
# pool_manager.py  —  Owns the primary and replica SQLAlchemy engines.
#                     Produces Sessions pointed at the right engine.
#
# SQLAlchemy difference from psycopg2:
#   - No manual borrow/release — Sessions are created via sessionmaker.
#   - The engine's QueuePool manages the underlying connections automatically.
#   - pool_pre_ping handles reconnection; we never touch raw connections here.
# =============================================================================

import logging
from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config._config import DBConfig
from app.config.database_engine import build_engine, ping_engine

logger = logging.getLogger(__name__)


class PoolManager:
    """
    Owns two SQLAlchemy engines (primary + optional replica).
    Vends sessionmaker factories so callers can open Sessions cleanly.

    Usage (via provider.py — don't call this directly):
        session = pool_manager.write_session()
        session = pool_manager.read_session()
    """

    def __init__(self, primary_cfg: DBConfig, replica_cfg: Optional[DBConfig] = None):
        # Build engines
        self._primary_engine: Engine = build_engine(primary_cfg, label="primary")
        self._replica_engine:  Optional[Engine] = (
            build_engine(replica_cfg, label="replica") if replica_cfg else None
        )

        if not replica_cfg:
            logger.warning("No replica config — all reads will go to primary.")

        # sessionmaker factories — bind= removed in SQLAlchemy 2.0, pass engine positionally
        # expire_on_commit=False: objects remain usable after session.commit()
        self._write_factory = sessionmaker(
            self._primary_engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        self._read_factory = sessionmaker(
            self._replica_engine or self._primary_engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    # ------------------------------------------------------------------
    # Session factories
    # ------------------------------------------------------------------

    def write_session(self) -> Session:
        """Open a new Session on the PRIMARY engine (for writes)."""
        return self._write_factory()

    def read_session(self) -> Session:
        """
        Open a new Session on the REPLICA engine (for reads).
        Falls back to primary engine if replica is not configured.
        """
        return self._read_factory()

    # ------------------------------------------------------------------
    # Engine access (for raw SQL via engine.connect())
    # ------------------------------------------------------------------

    @property
    def primary_engine(self) -> Engine:
        return self._primary_engine

    @property
    def replica_engine(self) -> Optional[Engine]:
        return self._replica_engine

    # ------------------------------------------------------------------
    # Health & stats
    # ------------------------------------------------------------------

    def health(self) -> dict:
        """Ping both engines and return their status."""
        result = {"primary": ping_engine(self._primary_engine, "primary")}
        if self._replica_engine:
            result["replica"] = ping_engine(self._replica_engine, "replica")
        else:
            result["replica"] = None
        return result

    def stats(self) -> dict:
        """Return live pool utilisation for monitoring."""
        def _pool_info(engine: Engine, label: str) -> dict:
            p = engine.pool
            return {
                "label":       label,
                # QueuePool 2.x attributes (all are plain properties, not callables)
                "pool_size":   p.size(),
                "checked_out": p.checkedout(),
                "overflow":    p.overflow(),
                "checked_in":  p.checkedin(),
            }

        result = {"primary": _pool_info(self._primary_engine, "primary")}
        if self._replica_engine:
            result["replica"] = _pool_info(self._replica_engine, "replica")
        return result

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def dispose_all(self) -> None:
        """
        Dispose both engine pools (closes all connections).
        Call once on application shutdown.
        """
        self._primary_engine.dispose()
        if self._replica_engine:
            self._replica_engine.dispose()
        logger.info("All engine pools disposed.")
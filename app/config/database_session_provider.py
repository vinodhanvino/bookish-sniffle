# =============================================================================
# provider.py  —  Thread-safe Singleton.
#                 Wraps PoolManager and exposes clean context managers.
#
# Two usage styles supported:
#   1. ORM  — yields a SQLAlchemy Session  (for model-based queries)
#   2. Core — yields a SQLAlchemy Connection (for raw SQL via text())
#
# Contains ZERO hardcoded values — all config comes from bootstrap.py.
# =============================================================================

import logging
import threading
from contextlib import contextmanager
from typing import Optional, Generator

from sqlalchemy.orm import Session
from sqlalchemy import Connection, text

from app.config._config import DBConfig, PRIMARY_CONFIG, REPLICA_CONFIG, REPLICA_FALLBACK
from app.config.database_pool_manager import PoolManager
# from router import is_write_query
import re

_WRITE_PATTERN = re.compile(
    r"^\s*(INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TRUNCATE|REPLACE|MERGE|CALL|EXEC)\b",
    re.IGNORECASE,
)


def is_write_query(sql: str) -> bool:
    """
    Return True if the SQL statement modifies data or schema.
    Return False for SELECT and other read-only statements.

    Examples:
        is_write_query("SELECT * FROM users")            → False
        is_write_query("INSERT INTO orders VALUES ...")  → True
        is_write_query("UPDATE users SET active=FALSE")  → True
        is_write_query("DROP TABLE temp")                → True
    """
    return bool(_WRITE_PATTERN.match(sql.lstrip()))


logger = logging.getLogger(__name__)


class ReadWriteSplitProvider:
    """
    Thread-safe Singleton provider.

    ORM-style  (recommended for model queries):
        with provider.write_session() as session:
            session.add(user)

        with provider.read_session() as session:
            users = session.query(User).filter_by(active=True).all()

    Core-style  (for raw SQL):
        with provider.write_conn() as conn:
            conn.execute(text("INSERT INTO logs (msg) VALUES (:msg)"), {"msg": "hello"})

        with provider.read_conn() as conn:
            result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})

    Auto-routing  (detects verb from SQL string):
        with provider.auto_conn("SELECT * FROM users") as conn: ...
        with provider.auto_conn("UPDATE users SET active=FALSE WHERE id=:id") as conn: ...
    """

    _instance: Optional["ReadWriteSplitProvider"] = None
    _lock: threading.Lock = threading.Lock()

    # ------------------------------------------------------------------
    # Singleton construction
    # ------------------------------------------------------------------

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(
            self,
            primary_config: Optional[DBConfig] = None,
            replica_config: Optional[DBConfig] = None,
            replica_fallback: bool = True,
    ):
        if self._initialized:
            return
        if primary_config is None:
            raise ValueError("primary_config is required on first call.")

        self._replica_fallback = replica_fallback
        self._pools = PoolManager(primary_config, replica_config)
        self._initialized = True
        logger.info("ReadWriteSplitProvider ready.")

    # ------------------------------------------------------------------
    # ORM-style: Session context managers
    # ------------------------------------------------------------------

    @contextmanager
    def write_session(self) -> Generator[Session, None, None]:
        """
        Yields a SQLAlchemy Session on the PRIMARY engine.
        Commits on clean exit, rolls back on exception, always closes.

        Best for: inserting / updating ORM model instances.

            with provider.write_session() as session:
                session.add(Order(user_id=1, total=99.0))
                # commits automatically
        """
        session: Session = self._pools.write_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Write session rolled back")
            raise
        finally:
            session.close()

    @contextmanager
    def read_session(self) -> Generator[Session, None, None]:
        """
        Yields a SQLAlchemy Session on the REPLICA engine.
        Never commits — always rolls back and closes.

        Best for: ORM queries that return model objects.

            with provider.read_session() as session:
                users = session.query(User).filter_by(active=True).all()
        """
        session: Session = self._pools.read_session()
        try:
            yield session
        except Exception:
            logger.exception("Read session error")
            raise
        finally:
            session.rollback()
            session.close()
    # ------------------------------------------------------------------
    # Core-style: Connection context managers (raw SQL)
    # ------------------------------------------------------------------

    @contextmanager
    def write_conn(self) -> Generator[Connection, None, None]:
        """
        Yields a SQLAlchemy Core Connection on the PRIMARY engine.
        Commits on clean exit, rolls back on exception.

        Best for: raw SQL writes, bulk inserts, DDL.

            with provider.write_conn() as conn:
                conn.execute(
                    text("INSERT INTO events (name) VALUES (:name)"),
                    {"name": "signup"}
                )
        """
        with self._pools.primary_engine.begin() as conn:
            # engine.begin() opens a transaction and auto-commits/rolls back
            yield conn

    @contextmanager
    def read_conn(self) -> Generator[Connection, None, None]:
        """
        Yields a SQLAlchemy Core Connection on the REPLICA engine.
        Read-only — no commit.

        Best for: raw SQL reads, aggregate queries, reporting.

            with provider.read_conn() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM orders WHERE status = :s"),
                    {"s": "pending"}
                )
                count = result.scalar()
        """
        engine = self._pools.replica_engine or self._pools.primary_engine
        with engine.connect() as conn:
            yield conn

    def save(self, obj) -> None:
        """
        Persist a single ORM object to the primary DB.

            provider.save(User(name="Alice"))
        """
        with self.write_session() as session:
            session.add(obj)
    def save_all(self, objs: list) -> None:
        """
        Persist multiple ORM objects in a single transaction.

            provider.save_all([User(name="Alice"), User(name="Bob")])
        """
        with self.write_session() as session:
            session.add_all(objs)
    @contextmanager
    def auto_conn(self, sql: str) -> Generator[Connection, None, None]:
        """
        Automatically routes to write_conn or read_conn based on the SQL verb.

        No need to decide manually — just pass the query string:

            with provider.auto_conn("SELECT id FROM users WHERE id = :id") as conn:
                row = conn.execute(text(sql), {"id": 1}).fetchone()

            with provider.auto_conn("UPDATE users SET name = :n WHERE id = :id") as conn:
                conn.execute(text(sql), {"n": "Alice", "id": 1})
        """
        if is_write_query(sql):
            with self.write_conn() as conn:
                yield conn
        else:
            with self.read_conn() as conn:
                yield conn

    # ------------------------------------------------------------------
    # Health & monitoring
    # ------------------------------------------------------------------

    def health_check(self) -> dict:
        """
        Ping both engines. Safe to expose on an internal /healthz endpoint.

        Returns:
            {
                "primary": True,
                "replica": True | False | None,
                "replica_fallback_active": False
            }
        """
        status = self._pools.health()
        status["replica_fallback_active"] = (
                self._pools.replica_engine is None and self._replica_fallback
        )
        return status

    @property
    def pool_stats(self) -> dict:
        """Live pool utilisation — how many connections are checked out."""
        return self._pools.stats()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def dispose_all(self) -> None:
        """Dispose all engine pools. Register with atexit or framework teardown."""
        self._pools.dispose_all()

    def __repr__(self) -> str:
        has_replica = self._pools.replica_engine is not None
        return (
            f"<ReadWriteSplitProvider "
            f"primary_pool={self._pools.primary_engine.pool.size()} "
            f"replica={'yes' if has_replica else 'none'}>"
        )


# ---------------------------------------------------------------------------
# Module-level factory  —  the only thing service code ever imports
# ---------------------------------------------------------------------------

def get_provider(
        primary_config: Optional[DBConfig] = None,
        replica_config: Optional[DBConfig] = None,
        replica_fallback: bool = True,
) -> ReadWriteSplitProvider:
    """
    Returns the Singleton provider.
    Pass configs only on the FIRST call (in bootstrap.py).
    All subsequent calls return the same instance — no re-initialisation.
    """
    return ReadWriteSplitProvider(
        primary_config=primary_config,
        replica_config=replica_config,
        replica_fallback=replica_fallback,
    )


if __name__ == "__main__":
    import atexit
    provider = get_provider(
        primary_config=PRIMARY_CONFIG,
        replica_config=REPLICA_CONFIG,
        replica_fallback=REPLICA_FALLBACK,
    )

    atexit.register(provider.dispose_all)

    print("DB provider ready: %s", provider)
    print("Pool stats: %s", provider.pool_stats)

    print("Health:", get_provider().health_check())
    print("Stats: ", get_provider().pool_stats)

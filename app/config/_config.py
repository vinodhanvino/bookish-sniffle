# =============================================================================
# config.py  —  ALL hardcoded values live here, nowhere else.
# Change DB hosts, credentials, and pool sizes only in this file.
#
# Dependencies:
#     pip install sqlalchemy psycopg2-binary
# =============================================================================

from dataclasses import dataclass, field
from app.settings import settings

@dataclass
class DBConfig:
    """
    Holds every setting needed to build one SQLAlchemy engine.
    One instance = one database host.
    """
    host: str
    database: str
    user: str
    password: str
    port: int = 5432
    driver: str = "postgresql+psycopg2"  # swap to asyncpg, pg8000, mysqldb, etc.

    # SQLAlchemy QueuePool settings
    pool_size: int = 10  # number of connections kept alive at steady state
    max_overflow: int = 20  # burst connections on top of pool_size
    pool_timeout: int = 30  # seconds to wait if pool is full before raising
    pool_recycle: int = 1800  # recycle connections older than 30 min (avoids stale sockets)
    pool_pre_ping: bool = True  # ping connection before use — auto-reconnects on failure

    # Any extra kwargs forwarded directly to create_engine()
    # e.g. {"echo": True} to log every SQL statement
    engine_kwargs: dict = field(default_factory=dict)

    @property
    def url(self) -> str:
        """SQLAlchemy database URL string."""
        return (
            f"{self.driver}://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


# -----------------------------------------------------------------------------
# PRIMARY  (handles all writes + reads when no replica is available)
# -----------------------------------------------------------------------------
PRIMARY_CONFIG = DBConfig(
    host=settings.HOST,
    database=settings.DATABASE,
    user=settings.USER,
    password=settings.PASSWORD,
    port=settings.PORT,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
)

# -----------------------------------------------------------------------------
# REPLICA  (handles read-only queries)
# -----------------------------------------------------------------------------
REPLICA_CONFIG = DBConfig(
    host=settings.HOST,
    database=settings.DATABASE,
    user=settings.USER,  # use a read-only Postgres role here
    password=settings.PASSWORD,
    port=settings.PORT,
    pool_size=settings.POOL_SIZE,  # replicas can absorb more concurrent reads
    max_overflow=settings.MAX_OVERFLOW,
)

# -----------------------------------------------------------------------------
# Behaviour flags
# -----------------------------------------------------------------------------
REPLICA_FALLBACK = True  # True  → reads fall back to primary when replica is down
# False → raise an error instead

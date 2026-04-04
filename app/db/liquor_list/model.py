"""ORM model for KSBCL master liquor rows (aligned with master-ksbcl.json `data` items)."""

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from app.config._config import PRIMARY_CONFIG, REPLICA_CONFIG, REPLICA_FALLBACK
from app.config.database_session_provider import get_provider

provider = get_provider(
    primary_config=PRIMARY_CONFIG,
    replica_config=REPLICA_CONFIG,
    replica_fallback=REPLICA_FALLBACK,
)
from app.db.base import Base


class LiquorList(Base):
    __tablename__ = "liquor_list"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_name: Mapped[str] = mapped_column(String(2048), nullable=False)
    kscl_price: Mapped[Decimal] = mapped_column(Numeric(16, 4), nullable=False)
    mrp: Mapped[Decimal] = mapped_column(Numeric(16, 4), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)


Base.metadata.create_all(bind=provider._pools.primary_engine, checkfirst=True)

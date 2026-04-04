from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.config._config import PRIMARY_CONFIG, REPLICA_CONFIG, REPLICA_FALLBACK
from app.config.database_session_provider import get_provider
from app.db.base import Base

provider = get_provider(
    primary_config=PRIMARY_CONFIG,
    replica_config=REPLICA_CONFIG,
    replica_fallback=REPLICA_FALLBACK,
)


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    more: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


Base.metadata.create_all(bind=provider._pools.primary_engine, checkfirst=True)

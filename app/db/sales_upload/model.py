from datetime import datetime

from sqlalchemy import DateTime, Integer, String
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


class SalesUploadReport(Base):
    __tablename__ = "sales"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_file_name = mapped_column(String(255), nullable=False)
    s3_path = mapped_column(String(255), nullable=False)
    outlet_name = ""
    source_file: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


Base.metadata.create_all(bind=provider._pools.primary_engine, checkfirst=True)

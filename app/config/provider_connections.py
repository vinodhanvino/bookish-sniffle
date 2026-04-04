"""Raw SQLAlchemy Connection routing (primary vs replica)."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import Connection, text

from app.config.sql_routing import is_write_query


class ConnectionMixin:
    """write_conn / read_conn / auto_conn."""

    _pools: object

    @contextmanager
    def write_conn(self) -> Generator[Connection, None, None]:
        with self._pools.primary_engine.begin() as conn:
            yield conn

    @contextmanager
    def read_conn(self) -> Generator[Connection, None, None]:
        engine = self._pools.replica_engine or self._pools.primary_engine
        with engine.connect() as conn:
            yield conn

    @contextmanager
    def auto_conn(self, sql: str) -> Generator[Connection, None, None]:
        if is_write_query(sql):
            with self.write_conn() as conn:
                yield conn
        else:
            with self.read_conn() as conn:
                yield conn

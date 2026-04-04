"""ORM Session helpers: write/read sessions and bulk save."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SessionMixin:
    """write_session / read_session / save / save_all."""

    _pools: object
    _initialized: bool

    @contextmanager
    def write_session(self) -> Generator[Session, None, None]:
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
        session: Session = self._pools.read_session()
        try:
            yield session
        except Exception:
            logger.exception("Read session error")
            raise
        finally:
            session.rollback()
            session.close()

    def save(self, obj) -> None:
        with self.write_session() as session:
            session.add(obj)

    def save_all(self, objs: list) -> None:
        with self.write_session() as session:
            session.add_all(objs)

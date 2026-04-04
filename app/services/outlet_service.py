from datetime import datetime

from app.config.database_session_provider import get_provider
from app.db.outlet import Outlet


def _row(o: Outlet) -> dict:
    return {
        "id": o.id,
        "outlet_name": o.outlet_name,
        "outlet_description": o.outlet_description,
        "created_by": o.created_by,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "modified_at": o.modified_at.isoformat() if o.modified_at else None,
        "archived": o.archived,
        "more": o.more or {},
    }


def create_outlet(
    outlet_name: str,
    outlet_description: str,
    created_by: int | None,
    more: dict,
) -> dict:
    with get_provider().write_session() as session:
        row = Outlet(
            outlet_name=outlet_name.strip(),
            outlet_description=outlet_description.strip(),
            created_by=created_by,
            more=more or {},
        )
        session.add(row)
        session.flush()
        session.refresh(row)
        return _row(row)


def get_outlet(outlet_id: int) -> dict | None:
    with get_provider().read_session() as session:
        o = session.query(Outlet).filter(Outlet.id == outlet_id).first()
    return _row(o) if o else None


def list_outlets(skip: int, limit: int, include_archived: bool) -> list[dict]:
    with get_provider().read_session() as session:
        q = session.query(Outlet)
        if not include_archived:
            q = q.filter(Outlet.archived.is_(False))
        rows = q.order_by(Outlet.id.desc()).offset(skip).limit(limit).all()
    return [_row(o) for o in rows]


def update_outlet(
    outlet_id: int,
    outlet_name: str | None,
    outlet_description: str | None,
    more: dict | None,
) -> dict | None:
    with get_provider().write_session() as session:
        o = session.query(Outlet).filter(Outlet.id == outlet_id).first()
        if not o:
            return None
        if outlet_name is not None:
            o.outlet_name = outlet_name.strip()
        if outlet_description is not None:
            o.outlet_description = outlet_description.strip()
        if more is not None:
            o.more = more
        o.modified_at = datetime.utcnow()
        session.flush()
        session.refresh(o)
        return _row(o)


def archive_outlet(outlet_id: int) -> dict | None:
    with get_provider().write_session() as session:
        o = session.query(Outlet).filter(Outlet.id == outlet_id).first()
        if not o:
            return None
        o.archived = True
        o.modified_at = datetime.utcnow()
        session.flush()
        session.refresh(o)
        return _row(o)

from fastapi import APIRouter, HTTPException, status

from app.schemas.outlet import (
    OutletArchive,
    OutletCreate,
    OutletGet,
    OutletList,
    OutletUpdate,
)
from app.services.outlet_service import (
    archive_outlet,
    create_outlet,
    get_outlet,
    list_outlets,
    update_outlet,
)

router = APIRouter(prefix="/outlet", tags=["outlet"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
def outlet_create(payload: OutletCreate) -> dict:
    return create_outlet(
        outlet_name=payload.outlet_name,
        outlet_description=payload.outlet_description,
        created_by=payload.created_by,
        more=payload.more,
    )


@router.post("/get", status_code=status.HTTP_200_OK)
def outlet_get(payload: OutletGet) -> dict:
    row = get_outlet(payload.id)
    if not row:
        raise HTTPException(status_code=404, detail="Outlet not found")
    return row


@router.post("/list", status_code=status.HTTP_200_OK)
def outlet_list(payload: OutletList) -> dict:
    items = list_outlets(
        skip=payload.skip,
        limit=payload.limit,
        include_archived=payload.include_archived,
    )
    return {"items": items, "count": len(items)}


@router.post("/update", status_code=status.HTTP_200_OK)
def outlet_update(payload: OutletUpdate) -> dict:
    row = update_outlet(
        outlet_id=payload.id,
        outlet_name=payload.outlet_name,
        outlet_description=payload.outlet_description,
        more=payload.more,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Outlet not found")
    return row


@router.post("/archive", status_code=status.HTTP_200_OK)
def outlet_archive(payload: OutletArchive) -> dict:
    row = archive_outlet(payload.id)
    if not row:
        raise HTTPException(status_code=404, detail="Outlet not found")
    return row

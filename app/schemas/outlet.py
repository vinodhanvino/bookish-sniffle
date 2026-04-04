from pydantic import BaseModel, Field

from app.settings import settings


class OutletCreate(BaseModel):
    outlet_name: str = Field(min_length=1, max_length=255)
    outlet_description: str = Field(min_length=1, max_length=1024)
    created_by: int | None = None
    more: dict = Field(default_factory=dict)


class OutletGet(BaseModel):
    id: int = Field(ge=1)


class OutletList(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(
        default=settings.OUTLET_LIST_DEFAULT_LIMIT,
        ge=1,
        le=settings.OUTLET_LIST_MAX_LIMIT,
    )
    include_archived: bool = False


class OutletUpdate(BaseModel):
    id: int = Field(ge=1)
    outlet_name: str | None = Field(default=None, min_length=1, max_length=255)
    outlet_description: str | None = Field(default=None, min_length=1, max_length=1024)
    more: dict | None = None


class OutletArchive(BaseModel):
    id: int = Field(ge=1)

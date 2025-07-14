from typing import Optional
from uuid import UUID

from app.schemas.base import BaseSchema


class RegionBase(BaseSchema):
    name: str


class RegionCreateRequest(BaseSchema):
    coordinate: Optional[str] = None
    name: str


class RegionCreateResponse(BaseSchema):
    id: UUID
    name: str
    coordinate: Optional[str] = None


class DistrictCreateRequest(BaseSchema):
    name: str
    coordinate: Optional[str] = None
    parent_region: UUID


class DistrictCreateResponse(BaseSchema):
    id: UUID
    name: str
    coordinate: Optional[str]
    parent_region: UUID
    parent_region_name: str


class DistrictBase(BaseSchema):
    name: str
    parent_region: int

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, validator
from app.schemas.base import BaseSchema


class SchoolBase(BaseSchema):
    name: str
    address: str
    region_id: int
    city_id: int
    district_id: int


class SchoolResponse(BaseSchema):
    id: int
    region_name: Optional[str]
    city_name: Optional[str]
    district_name: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class RegionResponse(BaseModel):
    id: int
    name: str


class CityResponse(BaseSchema):
    id: int
    name: str
    region_id: int


class DistrictResponse(BaseSchema):
    id: int
    name: str
    city_id: int

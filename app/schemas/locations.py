from app.schemas.base import BaseSchema


class RegionBase(BaseSchema):
    name: str


class RegionResponse(BaseSchema):
    id: int


class CityBase(BaseSchema):
    name: str
    parent_region: int


class CityResponse(BaseSchema):
    id: int


class DistrictBase(BaseSchema):
    name: str
    parent_region: int


class DistrictResponse(BaseSchema):
    id: int

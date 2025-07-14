from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.enums.enums import Genders, Shifts, UserRole
from app.schemas.base import BaseSchema


class SchoolCreate(BaseSchema):
    name: str
    address: str
    region_id: UUID
    district_id: UUID


class SchoolResponse(BaseSchema):
    id: UUID
    region_name: Optional[str]
    district_name: Optional[str]
    created_at: Optional[datetime]


class SchoolListResponse(BaseModel):
    id: UUID
    name: str
    address: str
    region_id: UUID
    region_name: Optional[str]
    district_id: UUID
    district_name: Optional[str]
    created_at: datetime


class RegionResponse(BaseModel):
    id: int
    name: str


class DistrictResponse(BaseSchema):
    id: int
    name: str


class UserCreateRequest(BaseSchema):
    phone_number: str
    username: str
    password: str
    role: UserRole

    @field_validator("phone_number", mode="before")
    def validate_phone_number(cls, v):
        v = v.strip()
        if not v.startswith("+998") or len(v) != 13 or not v[4:].isdigit():
            raise ValueError("Phone number must be in format +998XXXXXXXXX")
        return v


class UserRegisterResponse(BaseSchema):
    message: str
    user_id: UUID
    access_token: str
    token_type: str
    expires_at: int


class StudentInfoCreate(BaseSchema):
    user_id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str]
    age: int
    gender: Genders
    school: UUID
    shift: Shifts
    father: Optional[UUID]
    mother: Optional[UUID]


class ParentInfoCreate(BaseSchema):
    user_id: int
    first_name: str
    last_name: str
    patronymic: Optional[str]
    age: int
    gender: str
    passport_id: str


class UserPreferenceCreate(BaseSchema):
    user_id: int
    language: str
    theme: str


class IDResponse(BaseSchema):
    message: str
    id: UUID

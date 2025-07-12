from typing import Optional
from uuid import UUID

from pydantic import field_validator

from app.enums.enums import Genders, Shifts, UserRole
from app.schemas.base import BaseSchema


class UserCreate(BaseSchema):
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
    id: int

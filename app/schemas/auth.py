from uuid import UUID

from pydantic import field_validator

from app.enums.enums import UserRole
from app.schemas.base import BaseSchema


class PhoneNumberCheck(BaseSchema):
    phone_number: str
    user_role: UserRole

    @field_validator("phone_number", mode="before")
    def validate_phone_number(cls, v):
        v = v.strip()
        if not v.startswith("+998") or len(v) != 13 or not v[4:].isdigit():
            raise ValueError("Phone number must be in format +998XXXXXXXXX")
        return v


class PhoneNumberCheckResponse(BaseSchema):
    exists: bool
    message: str


class LoginRequest(BaseSchema):
    phone_number: str
    password: str

    @field_validator("phone_number", mode="before")
    def validate_phone_number(cls, v):
        v = v.strip()
        if not v.startswith("+998") or len(v) != 13 or not v[4:].isdigit():
            raise ValueError("Phone number must be in format +998XXXXXXXXX")
        return v


class LoginResponse(BaseSchema):
    access_token: str
    token_type: str
    user_id: int
    expires_at: int
    user_id: UUID
    user_role: UserRole

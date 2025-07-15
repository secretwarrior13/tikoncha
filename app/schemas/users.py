from typing import Optional
from uuid import UUID

from pydantic import field_validator

from app.enums.enums import Genders, Languages, Shifts, Themes, UserRole
from app.schemas.base import BaseSchema


class UserCreateRequest(BaseSchema):
    phone_number: str
    username: str
    password: str
    role: UserRole
    otp_send: bool = True


class UserCreateResponse(BaseSchema):
    id: UUID
    phone_number: str
    username: str
    user_role_name: str
    user_type_id: Optional[UUID] = None


class StudentInfoCreate(BaseSchema):
    user_id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    age: int
    gender: Genders
    school_id: UUID
    shift: Shifts
    father_id: Optional[UUID] = None
    mother_id: Optional[UUID] = None


class StudentInfoResponse(BaseSchema):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str]
    age: int
    gender: Genders
    school_id: UUID
    shift: Shifts
    father_id: Optional[UUID]
    mother_id: Optional[UUID]


class ParentInfoCreate(BaseSchema):
    user_id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    age: int
    gender: Genders
    passport_id: str


class ParentInfoResponse(BaseSchema):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    patronymic: Optional[str]
    age: int
    gender: Genders
    passport_id: str


class UserPreferenceCreate(BaseSchema):
    user_id: UUID
    language: Optional[Languages] = None
    theme: Optional[Themes] = None
    notifications_enabled: Optional[bool] = True


class UserPreferenceResponse(BaseSchema):
    id: UUID
    user_id: UUID
    language: Optional[Languages]
    theme: Optional[Themes]
    notifications_enabled: bool


class UserRegisterResponse(BaseSchema):
    message: str
    user_id: UUID
    otp_sent: bool


class OTPVerifyResponse(BaseSchema):
    message: str
    user_id: UUID


class IDResponse(BaseSchema):
    message: str
    id: UUID


class UserUpdate(BaseSchema):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None


class PhoneNumberCheck(BaseSchema):
    phone_number: str

    @field_validator("phone_number", mode="before")
    def validate_phone_number(cls, v):
        v = v.strip()
        if not v.startswith("+998") or len(v) != 13 or not v[4:].isdigit():
            raise ValueError("Phone number must be in format +998XXXXXXXXX")
        return v


class PhoneNumberCheckResponse(BaseSchema):
    exists: bool
    message: str


class SendOTPRequest(BaseSchema):
    phone_number: str


class VerifyOTPRequest(BaseSchema):
    phone_number: str
    code: str


class PendingRegisterResponse(BaseSchema):
    otp_sent: bool

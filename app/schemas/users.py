from datetime import datetime
from typing import Optional

from app.enums.enums import Genders, Languages, Themes, UserRole
from app.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    phone_number: str
    username: str
    password: str
    role: UserRole


class UserResponse(BaseSchema):
    id: int
    phone_number: str
    username: str
    user_type_id: int
    created_at: datetime
    updated_at: datetime


class StudentInfoCreate(BaseSchema):
    user_id: int
    first_name: str
    last_name: str
    patronymic: Optional[str]
    age: int
    gender: Genders
    school: str
    shift: str
    father: Optional[str]
    mother: Optional[str]


class StudentInfoResponse(BaseSchema):
    id: int


class ParentInfoCreate(BaseSchema):
    user_id: int
    first_name: str
    last_name: str
    patronymic: Optional[str]
    age: int
    gender: Genders
    passport_id: str


class ParentInfoResponse(BaseSchema):
    id: int


class UserPreferenceCreate(BaseSchema):
    user_id: int
    language: Optional[Languages]
    theme: Optional[Themes]
    notifications_enabled: Optional[bool] = None


class UserPreferenceResponse(BaseSchema):
    id: int

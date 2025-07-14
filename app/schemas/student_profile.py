from typing import Optional

from app.schemas.base import BaseSchema


class UserCreateResponse(BaseSchema):
    id: int
    phone_number: Optional[str]
    username: Optional[str]
    user_type: str


class StudentInfoResponse(BaseSchema):
    first_name: str
    last_name: str
    patronymic: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    shift: Optional[str]


class EducationResponse(BaseSchema):
    school_id: Optional[int]
    school_name: Optional[str]
    school_address: Optional[str]


class StudentProfileResponse(BaseSchema):
    user: UserCreateResponse
    student_info: StudentInfoResponse
    education: EducationResponse


class UpdateResponse(BaseSchema):
    message: str
    student_info: StudentInfoResponse
    education: EducationResponse


class StudentInfoUpdate(BaseSchema):

    first_name: Optional[str]
    last_name: Optional[str]
    patronymic: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    shift: Optional[str]
    school: Optional[int]

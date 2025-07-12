from typing import List, Optional
from pydantic import BaseModel, ConfigDict, validator
from app.enums.enums import Genders
from app.schemas.base import BaseSchema


class ParentProfileBase(BaseSchema):
    gender: Optional[Genders] = None
    address: Optional[str] = None


class ParentProfileUpdate(ParentProfileBase):
    pass


class ParentProfileResponse(BaseSchema):
    id: int
    user_id: int
    created_at: str
    updated_at: str


class ChildInfo(BaseSchema):
    id: int
    name: str
    age: int
    school: str


class ParentChildrenResponse(BaseSchema):
    message: str
    parent_id: int
    children: List[ChildInfo]

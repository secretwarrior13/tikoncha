# app/schemas/policies.py

from typing import Optional
from uuid import UUID

from app.schemas.base import BaseSchema


class PolicyCreateRequest(BaseSchema):
    name: str
    is_whitelist_app: bool = True
    is_whitelist_web: bool = True
    targeted_user_type_id: UUID


class PolicyCreateResponse(BaseSchema):
    id: UUID
    name: str
    is_whitelist_app: bool
    is_whitelist_web: bool
    targeted_user_type_id: UUID
    targeted_user_type_name: Optional[str]


class PolicyUpdateRequest(BaseSchema):
    name: Optional[str] = None
    is_whitelist_app: Optional[bool] = None
    is_whitelist_web: Optional[bool] = None
    targeted_user_type_id: Optional[UUID] = None


class PolicyRead(BaseSchema):
    id: UUID
    name: str
    is_whitelist_app: bool
    is_whitelist_web: bool
    targeted_user_type_id: UUID
    targeted_user_type_name: Optional[str]

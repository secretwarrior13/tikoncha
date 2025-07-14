from datetime import datetime
from typing import Dict, Optional

from app.enums.enums import AppType, GeneralType, Priorities
from app.schemas.base import BaseSchema


class AppBase(BaseSchema):
    name: str
    package_name: str
    general_type: Optional[GeneralType] = None
    app_type: Optional[AppType] = None
    priority: Optional[Priorities] = None


class AppResponse(BaseSchema):
    id: int
    installed: bool
    created_at: datetime
    updated_at: datetime


class InstalledAppResponse(BaseSchema):
    message: str
    app_id: int
    user_app_id: int


class AppRequestCreate(BaseSchema):
    app_id: int
    reason: str


class AppRequestResponse(BaseSchema):
    message: str
    request_id: int
    app_id: int
    app_name: str
    status: str
    created_at: datetime


class AppRequestListItem(BaseSchema):
    id: int
    app_id: int
    app_name: str
    reason: str
    status: str
    created_at: datetime
    updated_at: datetime


class TypesResponse(BaseSchema):
    general_types: Dict[str, str]
    app_types: Dict[str, str]
    priorities: Dict[str, str]


class UninstallResponse(BaseSchema):
    message: str
    app_id: int

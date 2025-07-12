from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.base import BaseSchema


class BlockedAppBase(BaseSchema):
    package_name: str
    app_name: str


class BlockedAppCreate(BaseSchema):
    pass


class BlockedAppResponse(BaseSchema):
    id: int
    is_blocked: bool


class EmergencyExceptionRequest(BaseSchema):
    app_id: int
    reason: str


class BlockingStatusResponse(BaseSchema):
    blocking_active: bool
    reason: str
    location_based: bool
    school_detected: str
    current_time: str
    is_holiday: bool
    shift: Optional[str]


class BlockedAppListItem(BaseSchema):
    id: int
    package_name: str
    app_name: str
    is_blocked: bool
    installed: bool
    category: str


class EmergencyExceptionResponse(BaseSchema):
    message: str
    status: str
    estimated_review_time: str
    app_id: int
    app_name: str
    reason: str


class SchoolScheduleItem(BaseModel):
    date: str
    name: str
    blocking_modified: Optional[bool]


class SchoolScheduleResponse(BaseSchema):
    month: int
    year: int
    school_id: int
    shift: Optional[str]
    holidays: List[SchoolScheduleItem]
    special_events: List[SchoolScheduleItem]

from typing import Optional, List
from app.schemas.base import BaseSchema


class LogBase(BaseSchema):
    device_id: int
    app_id: Optional[int] = None
    action_id: int
    duration: Optional[int] = None


class LogCreate(BaseSchema):
    pass


class DeviceInfo(BaseSchema):
    id: int
    name: str


class AppInfo(BaseSchema):
    id: int
    name: str
    package_name: str


class ActionInfo(BaseSchema):
    id: int
    name: str
    degree: Optional[str]


class LogDetail(BaseSchema):
    id: int
    user_id: int
    device: DeviceInfo
    app: Optional[AppInfo]
    action: ActionInfo
    duration: Optional[int]
    created_at: str


class ActionResponse(BaseSchema):
    id: int
    name: str
    degree: Optional[str]


class TopApp(BaseSchema):
    id: int
    name: str
    package_name: str
    usage_count: int
    total_duration: int


class LogSummaryResponse(BaseSchema):
    period_days: int
    start_date: str
    end_date: str
    total_logs: int
    suspicious_logs: int
    terrible_logs: int
    top_apps: List[TopApp]

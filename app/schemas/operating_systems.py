from uuid import UUID

from pydantic import UUID4, BaseModel

from app.enums.enums import AndroidUI, OsTypes
from app.schemas.base import BaseSchema


class OSBaseCreateRequest(BaseSchema):
    type: OsTypes
    version: str | None = None
    ui: AndroidUI | None = None
    ui_version: str | None = None


class OSUpdateRequest(BaseSchema):
    type: OsTypes | None = None
    version: str | None = None
    ui: AndroidUI | None = None
    ui_version: str | None = None


class OSResponse(BaseSchema):
    id: UUID


class IDResponse(BaseSchema):
    message: str
    id: UUID

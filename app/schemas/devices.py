from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.enums.enums import AndroidUI, PhoneBrands
from app.schemas.base import BaseSchema


class DeviceCreateRequest(BaseSchema):
    brand: PhoneBrands
    model: str
    os_id: str


class OSResponse(BaseSchema):
    id: int
    name: str
    version: str
    type: Optional[str]


class UserDeviceResponse(BaseSchema):
    user_device_id: int
    device_id: int
    device_name: str
    brand: Optional[str]
    model: str
    is_active: bool
    registered_at: str
    os: OSResponse
    android_ui: Optional[str]


class RegisterDeviceResponse(BaseSchema):
    message: str
    device_id: UUID
    user_device_id: UUID


class DeviceResponse(BaseSchema):
    id: UUID
    brand: Optional[str] = None
    model: str
    ram: Optional[int] = None
    storage: Optional[int] = None
    imei: Optional[str] = Field(None, alias="IMEI")
    os: OSResponse


class DeviceUpdateRequest(BaseModel):
    brand: Optional[PhoneBrands] = None
    model: Optional[str] = None
    os_id: Optional[UUID] = None
    ram: Optional[int] = None
    storage: Optional[int] = None
    imei: Optional[str] = Field(None)

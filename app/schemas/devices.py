from typing import Optional

from app.enums.enums import AndroidUI, PhoneBrands
from app.schemas.base import BaseSchema


class DeviceBase(BaseSchema):
    device_name: str
    brand: PhoneBrands
    model: str
    os_id: int
    android_ui: Optional[AndroidUI] = None

    class Config:
        from_attributes = True


class DeviceCreate(DeviceBase):
    """Same as DeviceBase – kept separate for clarity."""


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
    device_id: int
    user_device_id: int

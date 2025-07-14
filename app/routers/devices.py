# app/routers/device.py
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.devices import (
    DeviceCreate,
    OSResponse,
    RegisterDeviceResponse,
    UserDeviceResponse,
)
from app.services.devices import (
    deactivate_device,
    get_os_types,
    get_user_devices,
    register_device,
)

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("/my-devices", response_model=List[UserDeviceResponse])
async def read_my_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    return await get_user_devices(db, current_user)


@router.post("/register", response_model=RegisterDeviceResponse, status_code=201)
async def create_device(
    device_data: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    return await register_device(db, current_user, device_data)


@router.get("/os-types", response_model=List[OSResponse])
async def read_os_types(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),  # you can remove if not needed
):
    return await get_os_types(db)


@router.put("/{device_id}/deactivate", response_model=dict)
async def disable_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    return await deactivate_device(db, current_user, device_id)

# app/routers/device.py
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.models.users import User
from app.schemas.devices import (
    DeviceCreateRequest,
    DeviceResponse,
    DeviceUpdateRequest,
    OSResponse,
    RegisterDeviceResponse,
    UserDeviceResponse,
)
from app.services.devices import (
    DeviceResponse,
    deactivate_device,
    delete_device,
    list_all_devices,
    register_device,
    retrieve_device,
    update_device,
)

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("", response_model=List[DeviceResponse])
async def read_all_devices(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await list_all_devices(db)


@router.post("/register", response_model=RegisterDeviceResponse, status_code=201)
async def create_device(
    device_data: DeviceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    return await register_device(db, current_user, device_data)


@router.get("/{device_id}", response_model=DeviceResponse)
async def read_device(
    device_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    return await retrieve_device(db, current_user, device_id)


@router.put("/{device_id}/deactivate", response_model=dict)
async def disable_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    return await deactivate_device(db, current_user, device_id)


@router.put("/{device_id}", response_model=DeviceResponse)
async def edit_device(
    device_id: UUID,
    payload: DeviceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    return await update_device(db, current_user, device_id, payload)


@router.delete("/{device_id}", status_code=204)
async def remove_device(
    device_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    await delete_device(db, current_user, device_id)

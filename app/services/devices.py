from typing import List
<<<<<<< HEAD
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OS, Device, Setup, User, UserDevice
from app.schemas.devices import (
    DeviceCreateRequest,
    DeviceResponse,
    DeviceUpdateRequest,
=======

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import OS, Device, Setup, UserDevice
from app.models.user import User
from app.schemas.devices import (
    DeviceCreate,
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0
    OSResponse,
    RegisterDeviceResponse,
    UserDeviceResponse,
)


async def get_user_devices(
    db: AsyncSession, current_user: User
) -> List[UserDeviceResponse]:
    q = await db.execute(
        select(UserDevice).where(UserDevice.user_id == current_user.id)
    )
    ud_list = q.scalars().all()

    out: List[UserDeviceResponse] = []
    for ud in ud_list:
        dev = await db.get(Device, ud.device_id)
        os_obj = await db.get(OS, dev.os_id) if dev else None

        out.append(
            UserDeviceResponse(
                user_device_id=ud.id,
                device_id=dev.id,
                device_name=dev.device_name,
                brand=dev.brand.value if dev.brand else None,
                model=dev.model,
                is_active=ud.is_active,
                registered_at=ud.created_at.isoformat(),
                os=OSResponse(
                    id=os_obj.id,
                    name=os_obj.name,
                    version=os_obj.version,
                    type=os_obj.type.value if os_obj and os_obj.type else None,
                ),
                android_ui=dev.android_ui.value if dev.android_ui else None,
            )
        )
    return out


async def register_device(
    db: AsyncSession, current_user: User, data: DeviceCreateRequest
) -> RegisterDeviceResponse:
    os_obj = await db.get(OS, data.os_id)
    if not os_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "OS not found")

    new_dev = Device(
        brand=data.brand,
        model=data.model,
        os_id=data.os_id,
    )
    db.add(new_dev)
    await db.flush()

    ud = UserDevice(user_id=current_user.id, device_id=new_dev.id, is_active=True)
    db.add(ud)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not register device: {e}",
        )

    return RegisterDeviceResponse(
        message="Device registered successfully",
        device_id=new_dev.id,
        user_device_id=ud.id,
    )


async def get_os_types(db: AsyncSession) -> List[OSResponse]:
    q = await db.execute(select(OS))
    all_os = q.scalars().all()
    return [
        OSResponse(
            id=o.id,
            version=o.version,
            type=o.type.value if o.type else None,
        )
        for o in all_os
    ]


async def deactivate_device(
    db: AsyncSession, current_user: User, device_id: int
) -> dict:
    q = await db.execute(
        select(UserDevice)
        .where(UserDevice.user_id == current_user.id)
        .where(UserDevice.device_id == device_id)
    )
    ud = q.scalars().first()
    if not ud:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Device not found or does not belong to user",
        )

    ud.is_active = False
    await db.commit()
    return {"message": "Device deactivated successfully", "device_id": device_id}


async def list_all_devices(db: AsyncSession) -> list[DeviceResponse]:
    q = await db.execute(select(Device))
    devs = q.scalars().all()

    # bulk-load OS objects to avoid N+1 queries
    os_map = {o.id: o async for o in db.stream(select(OS))}
    return [
        DeviceResponse(
            id=d.id,
            brand=d.brand.value if d.brand else None,
            model=d.model,
            ram=d.ram,
            storage=d.storage,
            imei=d.IMEI,
            os=OSResponse(
                id=os_map[d.os_id].id,
                version=os_map[d.os_id].version,
                type=os_map[d.os_id].type.value if os_map[d.os_id].type else None,
            ),
        )
        for d in devs
    ]


async def retrieve_device(
    db: AsyncSession, current_user: User, device_id: UUID
) -> DeviceResponse:
    ud_row = (
        (
            await db.execute(
                select(UserDevice)
                .where(UserDevice.device_id == device_id)
                .where(UserDevice.user_id == current_user.id)
            )
        )
        .scalars()
        .first()
    )

    if not ud_row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Device not found")

    dev = await db.get(Device, device_id)
    os_obj = await db.get(OS, dev.os_id)
    return DeviceResponse(
        id=dev.id,
        brand=dev.brand.value if dev.brand else None,
        model=dev.model,
        ram=dev.ram,
        storage=dev.storage,
        imei=dev.IMEI,
        os=OSResponse(
            id=os_obj.id,
            version=os_obj.version,
            type=os_obj.type.value if os_obj.type else None,
        ),
    )


async def update_device(
    db: AsyncSession,
    current_user: User,
    device_id: UUID,
    data: DeviceUpdateRequest,
) -> DeviceResponse:
    # ownership check
    owned = (
        (
            await db.execute(
                select(UserDevice)
                .where(UserDevice.user_id == current_user.id)
                .where(UserDevice.device_id == device_id)
            )
        )
        .scalars()
        .first()
    )
    if not owned:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Device not found")

    dev: Device = await db.get(Device, device_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "imei":
            setattr(dev, "IMEI", value)
        else:
            setattr(dev, field, value)

    try:
        await db.commit()
    except IntegrityError as ie:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(ie)) from ie

    await db.refresh(dev)
    os_obj = await db.get(OS, dev.os_id)

    return DeviceResponse(
        id=dev.id,
        brand=dev.brand.value if dev.brand else None,
        model=dev.model,
        ram=dev.ram,
        storage=dev.storage,
        imei=dev.IMEI,
        os=OSResponse(
            id=os_obj.id,
            version=os_obj.version,
            type=os_obj.type.value if os_obj.type else None,
        ),
    )


async def delete_device(db: AsyncSession, current_user: User, device_id: UUID) -> dict:
    ud_row = (
        (
            await db.execute(
                select(UserDevice)
                .where(UserDevice.user_id == current_user.id)
                .where(UserDevice.device_id == device_id)
            )
        )
        .scalars()
        .first()
    )
    if not ud_row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Device not found")

    dev = await db.get(Device, device_id)
    await db.delete(dev)
    await db.commit()
    return {"message": "Device deleted", "device_id": str(device_id)}

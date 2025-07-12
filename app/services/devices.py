from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import OS, Device, Setup, UserDevice
from app.models.user import User
from app.schemas.devices import (
    DeviceCreate,
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
    db: AsyncSession, current_user: User, data: DeviceCreate
) -> RegisterDeviceResponse:
    os_obj = await db.get(OS, data.os_id)
    if not os_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "OS not found")

    new_dev = Device(
        device_name=data.device_name,
        brand=data.brand,
        model=data.model,
        os_id=data.os_id,
        android_ui=data.android_ui,
    )
    db.add(new_dev)
    await db.flush()

    ud = UserDevice(user_id=current_user.id, device_id=new_dev.id, is_active=True)
    db.add(ud)

    setup = Setup(user_id=current_user.id, device_id=new_dev.id, is_completed=False)
    db.add(setup)

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
            name=o.name,
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

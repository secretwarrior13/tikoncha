from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.enums import ActionDegrees
from app.models import Action
from app.models import App as AppModel
from app.models import Device, Log, User, UserApp, UserDevice, UserRole
from app.schemas.logs import (
    ActionInfo,
    ActionResponse,
    AppInfo,
    DeviceInfo,
    LogCreate,
    LogDetail,
    LogSummaryResponse,
    TopApp,
)


async def create_log(
    db: AsyncSession, current_user: User, data: LogCreate
) -> LogDetail:
    ud = (
        (
            await db.execute(
                select(UserDevice).where(
                    UserDevice.id == data.user_device_id,
                    UserDevice.user_id == current_user.id,
                )
            )
        )
        .scalars()
        .first()
    )
    if not ud:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Device does not belong to user")

    action = (
        (await db.execute(select(Action).where(Action.id == data.action_id)))
        .scalars()
        .first()
    )
    if not action:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Action not found")

    app_obj = None
    if data.user_app_id is not None:
        ua = (
            (await db.execute(select(UserApp).where(UserApp.id == data.user_app_id)))
            .scalars()
            .first()
        )
        if not ua:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "UserApp entry not found")
        # load the real App info
        app_obj = (
            (await db.execute(select(AppModel).where(AppModel.id == ua.app_id)))
            .scalars()
            .first()
        )

    new = Log(
        user_device_id=data.user_device_id,
        user_app_id=data.user_app_id,
        action_id=data.action_id,
        location=data.location,
        details=data.details,
    )
    db.add(new)
    await db.flush()
    await db.refresh(new)

    device = (
        (await db.execute(select(Device).where(Device.id == new.user_device_id)))
        .scalars()
        .first()
    )

    return LogDetail(
        id=new.id,
        user_device_id=new.user_device_id,
        user_app_id=new.user_app_id,
        device=DeviceInfo(id=device.id, name=device.device_name),
        app=(
            AppInfo(id=app_obj.id, name=app_obj.name, package_name=app_obj.package_name)
            if app_obj
            else None
        ),
        action=ActionInfo(
            id=action.id,
            name=action.name,
            degree=action.degree.value if action.degree else None,
        ),
        location=new.location,
        details=new.details,
        done_at=new.done_at.isoformat(),
    )


async def get_logs(
    db: AsyncSession,
    current_user: User,
    start_date: Optional[str],
    end_date: Optional[str],
    user_device_id: Optional[int],
    user_app_id: Optional[int],
    action_degree: Optional[str],
) -> List[LogDetail]:
    # permission check
    ut = (
        (
            await db.execute(
                select(UserRole).where(UserRole.id == current_user.user_type_id)
            )
        )
        .scalars()
        .first()
    )
    if not ut or ut.name not in ("parent", "admin"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Only parents/admins can view logs"
        )

    stmt = select(Log).join(UserDevice, Log.user_device_id == UserDevice.id)

    stmt = stmt.where(UserDevice.user_id == current_user.id)

    if start_date:
        try:
            sd = datetime.fromisoformat(start_date)
            stmt = stmt.where(Log.done_at >= sd)
        except ValueError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Invalid start_date format"
            )
    if end_date:
        try:
            ed = datetime.fromisoformat(end_date)
            stmt = stmt.where(Log.done_at <= ed)
        except ValueError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid end_date format")

    if user_device_id:
        stmt = stmt.where(Log.user_device_id == user_device_id)
    if user_app_id:
        stmt = stmt.where(Log.user_app_id == user_app_id)

    if action_degree:
        try:
            deg = ActionDegrees(action_degree)
            stmt = stmt.join(Action, Log.action_id == Action.id).where(
                Action.degree == deg
            )
        except ValueError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, f"Invalid action_degree: {action_degree}"
            )

    rows = (
        (await db.execute(stmt.order_by(Log.done_at.desc()).limit(100))).scalars().all()
    )

    out: List[LogDetail] = []
    for log in rows:
        device = (
            (await db.execute(select(Device).where(Device.id == log.user_device_id)))
            .scalars()
            .first()
        )

        app_info = None
        if log.user_app_id:
            ua = (
                (await db.execute(select(UserApp).where(UserApp.id == log.user_app_id)))
                .scalars()
                .first()
            )
            am = (
                (await db.execute(select(AppModel).where(AppModel.id == ua.app_id)))
                .scalars()
                .first()
            )
            app_info = AppInfo(id=am.id, name=am.name, package_name=am.package_name)

        action = (
            (await db.execute(select(Action).where(Action.id == log.action_id)))
            .scalars()
            .first()
        )

        out.append(
            LogDetail(
                id=log.id,
                user_device_id=log.user_device_id,
                user_app_id=log.user_app_id,
                device=DeviceInfo(id=device.id, name=device.device_name),
                app=app_info,
                action=ActionInfo(
                    id=action.id,
                    name=action.name,
                    degree=action.degree.value if action.degree else None,
                ),
                location=log.location,
                details=log.details,
                done_at=log.done_at.isoformat(),
            )
        )
    return out


async def get_actions(db: AsyncSession) -> List[ActionResponse]:
    actions = (await db.execute(select(Action))).scalars().all()
    return [
        ActionResponse(
            id=a.id, name=a.name, degree=a.degree.value if a.degree else None
        )
        for a in actions
    ]


async def get_log_summary(
    db: AsyncSession, current_user: User, days: int = 7
) -> LogSummaryResponse:
    ut = (
        (
            await db.execute(
                select(UserRole).where(UserRole.id == current_user.user_type_id)
            )
        )
        .scalars()
        .first()
    )
    if not ut or ut.name not in ("student", "parent", "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

    now = datetime.now()
    start = now - timedelta(days=days)

    total = await db.scalar(
        select(func.count(Log.id))
        .join(UserDevice, Log.user_device_id == UserDevice.id)
        .where(UserDevice.user_id == current_user.id, Log.done_at >= start)
    )
    suspicious = await db.scalar(
        select(func.count(Log.id))
        .join(UserDevice, Log.user_device_id == UserDevice.id)
        .join(Action, Log.action_id == Action.id)
        .where(
            UserDevice.user_id == current_user.id,
            Log.done_at >= start,
            Action.degree == ActionDegrees.suspicious,
        )
    )
    terrible = await db.scalar(
        select(func.count(Log.id))
        .join(UserDevice, Log.user_device_id == UserDevice.id)
        .join(Action, Log.action_id == Action.id)
        .where(
            UserDevice.user_id == current_user.id,
            Log.done_at >= start,
            Action.degree == ActionDegrees.terrible,
        )
    )

    top_rows = (
        await db.execute(
            select(
                AppModel.id,
                AppModel.name,
                AppModel.package_name,
                func.count(Log.id).label("usage_count"),
            )
            .join(UserApp, UserApp.id == Log.user_app_id)
            .join(AppModel, AppModel.id == UserApp.app_id)
            .join(UserDevice, Log.user_device_id == UserDevice.id)
            .where(UserDevice.user_id == current_user.id, Log.done_at >= start)
            .group_by(AppModel.id)
            .order_by(func.count(Log.id).desc())
            .limit(5)
        )
    ).all()

    top_apps = [
        TopApp(id=rid, name=rn, package_name=rp, usage_count=uc)
        for rid, rn, rp, uc in top_rows
    ]

    return LogSummaryResponse(
        period_days=days,
        start_date=start.isoformat(),
        end_date=now.isoformat(),
        total_logs=total or 0,
        suspicious_logs=suspicious or 0,
        terrible_logs=terrible or 0,
        top_apps=top_apps,
    )

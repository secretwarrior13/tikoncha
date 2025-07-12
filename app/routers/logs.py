# app/routers/logs.py
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.logs import (
    LogCreate,
    LogDetail,
    ActionResponse,
    LogSummaryResponse,
)
from app.services.logs import (
    create_log,
    get_logs,
    get_actions,
    get_log_summary,
)

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/", response_model=LogDetail, status_code=status.HTTP_201_CREATED)
async def post_log(
    log_data: LogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await create_log(db, current_user, log_data)


@router.get("/", response_model=List[LogDetail])
async def read_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    device_id: Optional[int] = None,
    app_id: Optional[int] = None,
    action_degree: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await get_logs(
        db, current_user, start_date, end_date, device_id, app_id, action_degree
    )


@router.get("/actions", response_model=List[ActionResponse])
async def read_actions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await get_actions(db)


@router.get("/summary", response_model=LogSummaryResponse)
async def read_summary(
    days: Optional[int] = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await get_log_summary(db, current_user, days)

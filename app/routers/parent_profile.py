from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.parent_profile import (
    ParentProfileResponse,
    ParentProfileUpdate,
    ParentChildrenResponse,
)
from app.services.parent_profile import (
    get_parent_profile,
    update_parent_profile,
    get_parent_children,
)

router = APIRouter(prefix="/parent", tags=["Parent"])


@router.get(
    "/profile",
    response_model=ParentProfileResponse,
)
async def read_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await get_parent_profile(db, current_user)


@router.put(
    "/profile",
    response_model=ParentProfileResponse,
)
async def put_profile(
    payload: ParentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await update_parent_profile(db, current_user, payload)


@router.get(
    "/children",
    response_model=ParentChildrenResponse,
)
async def read_children(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await get_parent_children(db, current_user)

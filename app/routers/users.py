from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.users import (
    ParentInfoResponse,
    StudentInfoResponse,
    UserPreferenceResponse,
    UserResponse,
)
from app.services.users import UserService

router = APIRouter(tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/student-info", response_model=StudentInfoResponse)
async def read_student_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = UserService(db)
    return await svc.get_student_info(current_user)


@router.get("/me/parent-info", response_model=ParentInfoResponse)
async def read_parent_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = UserService(db)
    return await svc.get_parent_info(current_user)


@router.get("/me/preferences", response_model=UserPreferenceResponse)
async def read_user_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = UserService(db)
    return await svc.get_preferences(current_user)

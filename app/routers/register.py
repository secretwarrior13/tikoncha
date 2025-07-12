# app/routers/users.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.schemas.register import (
    IDResponse,
    ParentInfoCreate,
    StudentInfoCreate,
    UserCreate,
    UserPreferenceCreate,
    UserRegisterResponse,
)
from app.services.register import (
    create_parent_info,
    create_student_info,
    create_user_preferences,
    register_user,
)

router = APIRouter(prefix="/register", tags=["Register"])


@router.post(
    "/create_user",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_new_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_async_session),
):
    return await register_user(db, payload)


@router.post(
    "/student-info", response_model=IDResponse, status_code=status.HTTP_201_CREATED
)
async def insert_student_info(
    payload: StudentInfoCreate,
    db: AsyncSession = Depends(get_async_session),
):
    return await create_student_info(db, payload)


@router.post(
    "/parent-info", response_model=IDResponse, status_code=status.HTTP_201_CREATED
)
async def parent_info_endpoint(
    payload: ParentInfoCreate,
    db: AsyncSession = Depends(get_async_session),
):
    return await create_parent_info(db, payload)


@router.post(
    "/preferences", response_model=IDResponse, status_code=status.HTTP_201_CREATED
)
async def preferences_endpoint(
    payload: UserPreferenceCreate,
    db: AsyncSession = Depends(get_async_session),
):
    return await create_user_preferences(db, payload)

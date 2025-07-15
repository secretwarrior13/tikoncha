from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.models.users import User
from app.schemas.preferences import UserPreferencesResponse
from app.services.preferences import (
    get_available_languages,
    get_available_themes,
    get_user_preferences,
    update_user_preferences,
    UserPreferencesUpdate
)

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get("/", response_model=UserPreferencesResponse)
async def read_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await get_user_preferences(db, current_user)


@router.put("/", response_model=UserPreferencesResponse)
async def put_preferences(
    payload: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await update_user_preferences(db, current_user, payload)


@router.get("/available-languages")
async def read_available_languages(
    current_user: User = Depends(get_current_user),
):
    return {"languages": await get_available_languages()}


@router.get("/available-themes")
async def read_available_themes(
    current_user: User = Depends(get_current_user),
):
    return {"themes": await get_available_themes()}

# app/services/preferences.py
from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.preferences import UserPreference
from app.models.users import User
from app.schemas.preferences import (
    Languages,
    Themes,
    UserPreferencesResponse,
    UserPreferencesUpdate,
)


async def get_user_preferences(db: AsyncSession, user: User) -> UserPreferencesResponse:
    pref = await db.get(UserPreference, user.id)
    if not pref:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found"
        )
    return UserPreferencesResponse(
        id=pref.id,
        user_id=pref.user_id,
        language=pref.language,
        theme=pref.theme,
        notifications_enabled=pref.notifications_enabled,
        created_at=pref.created_at.isoformat(),
        updated_at=pref.updated_at.isoformat(),
    )


async def update_user_preferences(
    db: AsyncSession, user: User, payload: UserPreferencesUpdate
) -> UserPreferencesResponse:
    pref = await db.get(UserPreference, user.id)
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.add(pref)

    # apply updates
    if payload.language is not None:
        pref.language = payload.language
    if payload.theme is not None:
        pref.theme = payload.theme
    if payload.notifications_enabled is not None:
        pref.notifications_enabled = payload.notifications_enabled

    try:
        await db.commit()
        await db.refresh(pref)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not update preferences: {e}",
        )

    return UserPreferencesResponse(
        id=pref.id,
        user_id=pref.user_id,
        language=pref.language,
        theme=pref.theme,
        notifications_enabled=pref.notifications_enabled,
        created_at=pref.created_at.isoformat(),
        updated_at=pref.updated_at.isoformat(),
    )


async def get_available_languages() -> Dict[str, str]:
    return {lang.name: lang.value for lang in Languages}


async def get_available_themes() -> Dict[str, str]:
    return {theme.name: theme.value for theme in Themes}

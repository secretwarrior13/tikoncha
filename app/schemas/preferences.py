# app/schemas/preferences.py
from typing import Optional

from app.enums.enums import Languages, Themes
from app.schemas.base import BaseSchema


class UserPreferencesBase(BaseSchema):
    """Shared fields for preferences"""

    language: Optional[Languages] = None
    theme: Optional[Themes] = None
    notifications_enabled: Optional[bool] = None


class UserPreferencesUpdate(UserPreferencesBase):
    """Payload for PUT /preferences"""



class UserPreferencesResponse(UserPreferencesBase):
    """Response for GET /preferences"""

    id: int
    user_id: int
    created_at: str
    updated_at: str

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    oauth2_scheme,
    verify_password,
)
from app.models.users import User
from app.schemas.auth import LoginResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/token",
    response_model=LoginResponse,
    include_in_schema=False,
)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await AuthService(db).authenticate_user(
        db,
        phone_number=form_data.username,
        password=form_data.password,
    )
    access_token, expires_at = create_access_token(
        data={"sub": str(user.id), "role": user.user_role_name}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user_id": user.id,
        "user_role": user.user_role_name,
    }

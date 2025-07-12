from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    PhoneNumberCheck,
    PhoneNumberCheckResponse,
    LoginRequest,
    LoginResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/user-exists",
    response_model=PhoneNumberCheckResponse,
)
async def check_user_exists(
    data: PhoneNumberCheck,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.check_user_exists(data.phone_number, data.user_role)

@router.post(
    "/log_in", response_model=LoginResponse, summary="Log in or refresh token"
)
async def log_in(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    token_data = await service.login(
        data.phone_number, data.password
    )
    return token_data

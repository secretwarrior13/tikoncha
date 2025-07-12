from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.enums.enums import UserRole
from app.schemas.auth import (PhoneNumberCheckResponse,
                             LoginRequest, LoginResponse)
from sqlalchemy import select, and_

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_user_exists(
        self, phone_number: str, user_role: UserRole
    ) -> PhoneNumberCheckResponse:
        stmt = select(User).where(
            and_(
                User.phone_number == phone_number,
                User.user_role_name == user_role.value
            )
        )
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please register."
            )
        return PhoneNumberCheckResponse(
            exists=True,
            message="User exists. Please proceed to login."
        )

    async def authenticate_user(self, phone_number: str, password: str) -> User:
        stmt = select(User).where(User.phone_number == phone_number)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect phone number or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def login(self, phone_number: str, password: str) -> dict:
        user = await self.authenticate_user(phone_number, password)
        access_token, expires_at = create_access_token(
            data={"sub": str(user.id), "role": user.user_role_name}
        )
        return {
            "access_token": access_token,
            "token_type":   "bearer",
            "user_id":      user.id,
            "user_role":    user.user_role_name,
            "expires_at":   expires_at,
        }
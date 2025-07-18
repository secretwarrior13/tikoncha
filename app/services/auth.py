from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.enums.enums import UserRole
from app.models.users import User
from app.schemas.users import PhoneNumberCheckResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(
        self, db: AsyncSession, phone_number: str, password: str
    ) -> User:
        user = await db.scalar(select(User).where(User.phone_number == phone_number))
        if user is None:
            print("LOGIN-FAIL: user not found →", phone_number)
            raise HTTPException(status_code=401)

        if not verify_password(password, user.password_hash):
            print("LOGIN-FAIL: bad password for", phone_number)
            raise HTTPException(status_code=401)

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
            "token_type": "bearer",
            "user_id": user.id,
            "user_role": user.user_role_name,
            "expires_at": expires_at,
        }

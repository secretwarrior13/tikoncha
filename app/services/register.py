from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import config, create_access_token, hash_password
from app.models.preferences import UserPreference
from app.models.user import ParentInfo, StudentInfo, User
from app.schemas.register import (
    IDResponse,
    ParentInfoCreate,
    StudentInfoCreate,
    UserCreate,
    UserPreferenceCreate,
    UserRegisterResponse,
)


async def register_user(db: AsyncSession, data: UserCreate) -> UserRegisterResponse:
    stmt = select(User).where(
        User.phone_number == data.phone_number, User.user_role_name == data.role.name
    )
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Phone already registered for this role"
        )

    new_user = User(
        phone_number=data.phone_number,
        username=data.username,
        user_role_name=data.role.value,
        password_hash=hash_password(data.password),
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"Registration failed: {e.orig}"
        )

    access_token = ""
    expires_at = 0
    try:
        token_data = {
            "sub": str(new_user.id),
            "phone": new_user.phone_number,
            "role": new_user.user_role_name,
        }
        expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, expires_at = create_access_token(
            token_data, expires_delta=expires
        )
    except Exception as e:
        print("⚠️ Token generation failed:", e)

    return UserRegisterResponse(
        message="User registered successfully",
        user_id=new_user.id,
        access_token=access_token,
        token_type="bearer" if access_token else "",
        expires_at=expires_at,
    )


async def create_student_info(db: AsyncSession, data: StudentInfoCreate) -> IDResponse:
    user = (
        (await db.execute(select(User).where(User.id == data.user_id)))
        .scalars()
        .first()
    )
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    exists = (
        (
            await db.execute(
                select(StudentInfo).where(StudentInfo.user_id == data.user_id)
            )
        )
        .scalars()
        .first()
    )
    if exists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Student info already exists")

    new = StudentInfo(**data.dict())
    db.add(new)
    try:
        await db.commit()
        await db.refresh(new)
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Creation failed: {e.orig}")

    return IDResponse(message="Student info created", id=new.id)


async def create_parent_info(db: AsyncSession, data: ParentInfoCreate) -> IDResponse:
    user = (
        (await db.execute(select(User).where(User.id == data.user_id)))
        .scalars()
        .first()
    )
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    exists = (
        (await db.execute(select(ParentInfo).where(ParentInfo.user_id == data.user_id)))
        .scalars()
        .first()
    )
    if exists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Parent info already exists")

    new = ParentInfo(**data.dict())
    db.add(new)
    try:
        await db.commit()
        await db.refresh(new)
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Creation failed: {e.orig}")

    return IDResponse(message="Parent info created", id=new.id)


async def create_user_preferences(
    db: AsyncSession, data: UserPreferenceCreate
) -> IDResponse:
    user = (
        (await db.execute(select(User).where(User.id == data.user_id)))
        .scalars()
        .first()
    )
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    exists = (
        (
            await db.execute(
                select(UserPreference).where(UserPreference.user_id == data.user_id)
            )
        )
        .scalars()
        .first()
    )
    if exists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Preferences already exist for this user"
        )

    new = UserPreference(**data.dict())
    db.add(new)
    try:
        await db.commit()
        await db.refresh(new)
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Creation failed: {e.orig}")

    return IDResponse(message="User preferences created", id=new.id)

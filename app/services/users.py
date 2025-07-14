<<<<<<< HEAD
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.otp_send import send_otp
from app.core.security import config, create_access_token, hash_password
from app.enums.enums import UserRole
from app.models import OTPEntry, ParentInfo, PendingUser, StudentInfo, User
from app.models.preferences import UserPreference
from app.schemas.users import (
    IDResponse,
    OTPVerifyResponse,
    ParentInfoCreate,
    ParentInfoResponse,
    PendingRegisterResponse,
    PhoneNumberCheckResponse,
    StudentInfoCreate,
    StudentInfoResponse,
    UserCreateRequest,
    UserCreateResponse,
    UserPreferenceCreate,
    UserPreferenceResponse,
    UserRegisterResponse,
    UserUpdate,
)
=======
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.preferences import UserPreference
from app.models.user import ParentInfo, StudentInfo, UserType
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_user_exists(self, phone_number: str) -> PhoneNumberCheckResponse:
        try:
            stmt = select(User).where(User.phone_number == phone_number)
            result = await self.db.execute(stmt)
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, "User not found. Please register."
                )
            return PhoneNumberCheckResponse(
                exists=True, message="User exists. Please proceed to login."
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error checking user existence: {e}",
            )

    async def get_user_profile(
        self, current_user: User, target_user_id: Optional[UUID] = None
    ) -> User:
        try:
            user_id = target_user_id or current_user.id
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, f"User {user_id} not found"
                )
            return user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error retrieving user profile: {e}",
            )

    async def register_user(self, data: UserCreateRequest) -> UserRegisterResponse:

        if data.otp_send:
            await self.db.execute(
                delete(PendingUser).where(PendingUser.phone_number == data.phone_number)
            )
            pending = PendingUser(
                phone_number=data.phone_number,
                username=data.username,
                password_hash=hash_password(data.password),
                role_name=data.role.value,
                created_at=datetime.utcnow(),
            )
            self.db.add(pending)
            await self.db.flush()

            code = f"{secrets.randbelow(10 ** 6):06d}"
            hash_ = hashlib.sha256(code.encode()).hexdigest()
            expires = datetime.utcnow() + timedelta(minutes=5)
            otp_entry = OTPEntry(
                pending_user_id=pending.id,
                phone_number=data.phone_number,
                code_hash=hash_,
                expires_at=expires,
            )
            self.db.add(otp_entry)
            await self.db.commit()

            await send_otp(data.phone_number, f"Your verification code is {code}")

            return UserRegisterResponse(
                message="OTP sent. Please verify.",
                user_id=pending.id,
                otp_sent=True,
            )

        user = User(
            phone_number=data.phone_number,
            username=data.username,
            user_role_name=data.role.value,
            password_hash=hash_password(data.password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return UserRegisterResponse(
            message="User registered successfully",
            user_id=user.id,
            otp_sent=False,
        )

    async def update_user(
        self,
        current_user: User,
        data: UserUpdate,
        target_user_id: Optional[UUID] = None,
    ) -> UserCreateResponse:
        try:
            user_id = target_user_id or current_user.id
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, f"User {user_id} not found"
                )

            update_data = data.dict(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "No fields provided to update"
                )
            if "password" in update_data:
                update_data["password_hash"] = hash_password(
                    update_data.pop("password")
                )

            for field, value in update_data.items():
                setattr(user, field, value)

            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return UserCreateResponse.from_orm(user)
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error updating user: {e}"
            )

    async def delete_user(
        self,
        current_user: User,
        target_user_id: Optional[UUID] = None,
    ) -> None:
        try:
            user_id = target_user_id or current_user.id
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, f"User {user_id} not found"
                )
            await self.db.delete(user)
            await self.db.commit()
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error deleting user: {e}"
            )

    async def get_student_info(
        self, current_user: User, target_user_id: Optional[UUID] = None
    ) -> StudentInfo:
        try:
            user_id = target_user_id or current_user.id
            if (
                target_user_id is None
                and current_user.user_role_name.lower() != UserRole.STUDENT.value
            ):
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN,
                    "Access denied. Only students can fetch their own info.",
                )

            stmt = select(StudentInfo).where(StudentInfo.user_id == user_id)
            result = await self.db.execute(stmt)
            si = result.scalars().first()
            if not si:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    f"Student information not found for user {user_id}",
                )
            return si
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error fetching student info: {e}",
            )

    async def update_student_info(
        self, current_user: User, data: StudentInfoCreate
    ) -> StudentInfoResponse:
        try:
            si = await self.get_student_info(current_user, current_user.id)
            for k, v in data.dict(exclude_unset=True).items():
                setattr(si, k, v)
            self.db.add(si)
            await self.db.commit()
            await self.db.refresh(si)
            return StudentInfoResponse.from_orm(si)
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error updating student info: {e}",
            )

    async def delete_student_info_by_user_id(self, user_id: UUID) -> None:
        try:
            stmt = select(StudentInfo).where(StudentInfo.user_id == user_id)
            result = await self.db.execute(stmt)
            si = result.scalars().first()
            if not si:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Student info not found")
            await self.db.delete(si)
            await self.db.commit()
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error deleting student info: {e}",
            )

    async def create_student_info(self, data: StudentInfoCreate) -> IDResponse:
        try:
            stmt = select(User).where(User.id == data.user_id)
            user = (await self.db.execute(stmt)).scalars().first()
            if not user:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

            stmt = select(StudentInfo).where(StudentInfo.user_id == data.user_id)
            exists = (await self.db.execute(stmt)).scalars().first()
            if exists:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Student info already exists"
                )

            new = StudentInfo(**data.dict())
            self.db.add(new)
            try:
                await self.db.commit()
                await self.db.refresh(new)
            except IntegrityError:
                await self.db.rollback()
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Creation failed: duplicate entry"
                )
            return IDResponse(message="Student info created", id=new.id)
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error creating student info: {e}",
            )

    async def get_parent_info(self, current_user: User) -> ParentInfo:
        try:
            stmt = select(ParentInfo).where(ParentInfo.user_id == current_user.id)
            result = await self.db.execute(stmt)
            pi = result.scalars().first()
            if not pi:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    "Parent information not found for this user",
                )
            return pi
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error fetching parent info: {e}",
            )

    async def update_parent_info(
        self, current_user: User, data: ParentInfoCreate
    ) -> ParentInfoResponse:
        try:
            pi = await self.get_parent_info(current_user)
            for k, v in data.dict(exclude_unset=True).items():
                setattr(pi, k, v)
            self.db.add(pi)
            await self.db.commit()
            await self.db.refresh(pi)
            return ParentInfoResponse.from_orm(pi)
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error updating parent info: {e}",
            )

    async def delete_parent_info(self, current_user: User) -> None:
        try:
            pi = await self.get_parent_info(current_user)
            await self.db.delete(pi)
            await self.db.commit()
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error deleting parent info: {e}",
            )

    async def create_parent_info(self, data: ParentInfoCreate) -> IDResponse:
        try:
            stmt = select(User).where(User.id == data.user_id)
            user = (await self.db.execute(stmt)).scalars().first()
            if not user:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

            stmt = select(ParentInfo).where(ParentInfo.user_id == data.user_id)
            exists = (await self.db.execute(stmt)).scalars().first()
            if exists:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Parent info already exists"
                )

            new = ParentInfo(**data.dict())
            self.db.add(new)
            try:
                await self.db.commit()
                await self.db.refresh(new)
            except IntegrityError:
                await self.db.rollback()
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Creation failed: duplicate entry"
                )
            return IDResponse(message="Parent info created", id=new.id)
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error creating parent info: {e}",
            )

    async def get_preferences(
        self, current_user: User, target_user_id: Optional[UUID] = None
    ) -> UserPreference:
        try:
            user_id = target_user_id or current_user.id
            stmt = select(UserPreference).where(UserPreference.user_id == user_id)
            result = await self.db.execute(stmt)
            pref = result.scalars().first()
            if not pref:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    f"Preferences not found for user {user_id}",
                )
            return pref
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error fetching preferences: {e}",
            )

    async def update_preferences(
        self, current_user: User, data: UserPreferenceCreate
    ) -> UserPreferenceResponse:
        try:
            pref = await self.get_preferences(current_user, current_user.id)
            for k, v in data.dict(exclude_unset=True).items():
                setattr(pref, k, v)
            self.db.add(pref)
            await self.db.commit()
            await self.db.refresh(pref)
            return UserPreferenceResponse.from_orm(pref)
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error updating preferences: {e}",
            )

    async def delete_preferences(
        self, current_user: User, target_user_id: Optional[UUID] = None
    ) -> None:
        try:
            user_id = target_user_id or current_user.id
            stmt = select(UserPreference).where(UserPreference.user_id == user_id)
            result = await self.db.execute(stmt)
            pref = result.scalars().first()
            if not pref:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    f"Preferences not found for user {user_id}",
                )
            await self.db.delete(pref)
            await self.db.commit()
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error deleting preferences: {e}",
            )

    async def create_user_preferences(self, data: UserPreferenceCreate) -> IDResponse:
        try:
            stmt = select(User).where(User.id == data.user_id)
            user = (await self.db.execute(stmt)).scalars().first()
            if not user:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

            stmt = select(UserPreference).where(UserPreference.user_id == data.user_id)
            exists = (await self.db.execute(stmt)).scalars().first()
            if exists:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "Preferences already exist for this user",
                )

            new = UserPreference(**data.dict())
            self.db.add(new)
            try:
                await self.db.commit()
                await self.db.refresh(new)
            except IntegrityError:
                await self.db.rollback()
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Creation failed: duplicate entry"
                )

            return IDResponse(message="User preferences created", id=new.id)
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error creating preferences: {e}",
            )

    async def send_otp(self, phone_number: str) -> None:
        code = f"{secrets.randbelow(10**6):06d}"
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        expires = datetime.utcnow() + timedelta(minutes=5)

        otp = OTPEntry(
            phone_number=phone_number, code_hash=code_hash, expires_at=expires
        )
        self.db.add(otp)
        await self.db.commit()

        await send_otp(phone_number, f"Your OTP code is: {code}")

    async def verify_otp_and_create_user(
        self, phone_number: str, code: str
    ) -> OTPVerifyResponse:
        stmt = (
            select(OTPEntry)
            .where(OTPEntry.phone_number == phone_number, OTPEntry.used == False)
            .order_by(OTPEntry.expires_at.desc())
        )
        result = await self.db.execute(stmt)
        otp: OTPEntry = result.scalars().first()

        if not otp or otp.expires_at < datetime.utcnow():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "OTP expired or not found")

        if hashlib.sha256(code.encode()).hexdigest() != otp.code_hash:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid OTP code")

        otp.used = True
        self.db.add(otp)

        stmt = select(PendingUser).where(PendingUser.phone_number == phone_number)
        result = await self.db.execute(stmt)
        pending: PendingUser = result.scalars().first()
        if not pending:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Pending registration not found"
            )

        user = User(
            phone_number=pending.phone_number,
            username=pending.username,
            password_hash=pending.password_hash,
            user_role_name=pending.role_name,
        )
        self.db.add(user)

        await self.db.delete(pending)

        await self.db.commit()
        await self.db.refresh(user)

        return OTPVerifyResponse(
            message="User verified and created successfully",
            user_id=user.id,
        )

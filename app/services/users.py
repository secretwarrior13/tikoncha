from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import StudentInfo, ParentInfo, UserType
from app.models.preferences import UserPreference


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_student_info(self, user) -> StudentInfo:
        # ensure user is a student
        ut = await self.db.get(UserType, user.user_type_id)
        if not ut or ut.name != "student":
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "Access denied. Only students."
            )
        result = await self.db.execute(select(StudentInfo).filter_by(user_id=user.id))
        si = result.scalars().first()
        if not si:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Student information not found for this user"
            )
        return si

    async def get_parent_info(self, user) -> ParentInfo:
        result = await self.db.execute(select(ParentInfo).filter_by(user_id=user.id))
        pi = result.scalars().first()
        if not pi:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Parent information not found for this user"
            )
        return pi

    async def get_preferences(self, user) -> UserPreference:
        result = await self.db.execute(
            select(UserPreference).filter_by(user_id=user.id)
        )
        pref = result.scalars().first()
        if not pref:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Preferences not found for this user"
            )
        return pref

# app/students/service.py
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import School, StudentInfo, UserRole
from app.schemas.student_profile import (
    EducationResponse,
    StudentInfoResponse,
    StudentInfoUpdate,
    StudentProfileResponse,
    UpdateResponse,
    UserCreateResponse,
)


class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _ensure_student(self, user) -> StudentInfo:
        ut = await self.db.get(UserRole, user.user_type_id)
        if user.user_role_name.lower() != "student":
            raise HTTPException(403, "Only students")

        si = (
            await self.db.execute(select(StudentInfo).filter_by(user_id=user.id))
        ).scalar_one_or_none()
        if not si:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found",
            )
        return si

    async def get_profile(self, user) -> StudentProfileResponse:
        si = await self._ensure_student(user)

        school = None
        if si.school_id:
            school = await self.db.get(School, si.school_id)

        user_type_name = user.user_role_name
        if user.user_type_id:
            ut = await self.db.get(UserRole, user.user_type_id)
            if ut and ut.name:
                user_type_name = ut.name

        return StudentProfileResponse(
            user=UserCreateResponse(
                id=user.id,
                phone_number=user.phone_number,
                username=user.username,
                user_type=user_type_name,
            ),
            student_info=StudentInfoResponse(
                first_name=si.first_name,
                last_name=si.last_name,
                patronymic=si.patronymic,
                age=si.age,
                gender=si.gender.value if si.gender else None,
                shift=si.shift.value if si.shift else None,
            ),
            education=EducationResponse(
                school_id=si.school_id,
                school_name=school.name if school else None,
                school_address=school.address if school else None,
            ),
        )

    async def update_info(self, data: StudentInfoUpdate, user) -> UpdateResponse:
        si = await self._ensure_student(user)
        update_data = data.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(si, field, val)
        await self.db.commit()
        await self.db.refresh(si)

        school = None
        if si.school:
            school = await self.db.get(School, si.school)

        return UpdateResponse(
            message="Student information updated successfully",
            student_info=StudentInfoResponse(
                first_name=si.first_name,
                last_name=si.last_name,
                patronymic=si.patronymic,
                age=si.age,
                gender=si.gender.value if si.gender else None,
                shift=si.shift.value if si.shift else None,
            ),
            education=EducationResponse(
                school_id=si.school,
                school_name=school.name if school else None,
                school_address=school.address if school else None,
            ),
        )

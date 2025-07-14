from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.schemas.student_profile import (
    StudentInfoUpdate,
    StudentProfileResponse,
    UpdateResponse,
)
from app.services.student_profile import StudentService

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/profile", response_model=StudentProfileResponse)
async def get_student_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = StudentService(db)
    return await svc.get_profile(current_user)


@router.put("/update", response_model=UpdateResponse)
async def update_student_info(
    student_data: StudentInfoUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = StudentService(db)
    return await svc.update_info(student_data, current_user)

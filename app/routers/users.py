import logging
import traceback
from typing import Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.exc import LoggedHTTPException, raise_with_log
from app.models.users import User
from app.schemas.users import (
    IDResponse,
    OTPVerifyResponse,
    PendingRegisterResponse,
    PhoneNumberCheck,
    PhoneNumberCheckResponse,
    SendOTPRequest,
    StudentInfoCreate,
    StudentInfoResponse,
    UserCreateRequest,
    UserCreateResponse,
    UserPreferenceCreate,
    UserPreferenceResponse,
    UserRegisterResponse,
    UserUpdate,
    VerifyOTPRequest,
)
from app.services.users import UserService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/users")


@router.post("/user-exists", response_model=PhoneNumberCheckResponse, tags=["Users"])
async def check_user_exists(
    data: PhoneNumberCheck,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        return await svc.check_user_exists(data.phone_number)

    except HTTPException:
        raise

    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to check user existence: {e}." + traceback.format_exc(),
        )


@router.post(
    "/create",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
async def register_user(
    payload: UserCreateRequest,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        return await svc.register_user(payload)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to register user: {e}." + traceback.format_exc(),
        )


@router.post(
    "/verify-otp",
    response_model=OTPVerifyResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
async def verify_otp(
    data: VerifyOTPRequest,
    db: AsyncSession = Depends(get_async_session),
):

    service = UserService(db)
    return await service.verify_otp_and_create_user(
        phone_number=data.phone_number,
        code=data.code,
    )


@router.get("/", response_model=UserCreateResponse, tags=["Users"])
async def get_user(
    user_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        return await svc.get_user_profile(current_user, user_id)
    except HTTPException:
        raise

    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to retrieve user: {e}." + traceback.format_exc(),
        )


@router.put("/", response_model=UserCreateResponse, tags=["Users"])
async def update_user(
    payload: UserUpdate,
    user_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        return await svc.update_user(
            current_user=current_user,
            data=payload,
            target_user_id=user_id,
        )
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to update user: {e}." + traceback.format_exc(),
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def delete_user(
    user_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        await svc.delete_user(current_user=current_user, target_user_id=user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to delete user: {e}." + traceback.format_exc(),
        )


@router.post(
    "/student-info",
    response_model=IDResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users - Student Info"],
)
async def create_student_info(
    payload: StudentInfoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        return await svc.create_student_info(payload)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to create student info: {e}." + traceback.format_exc(),
        )


@router.get(
    "/student-info", response_model=StudentInfoResponse, tags=["Users - Student Info"]
)
async def get_student_info(
    user_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        return await svc.get_student_info(current_user, user_id)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to retrieve student info: {e}." + traceback.format_exc(),
        )


@router.put(
    "/student-info", response_model=StudentInfoResponse, tags=["Users - Student Info"]
)
async def update_student_info(
    payload: StudentInfoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        return await svc.update_student_info(current_user, payload)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to update student info: {e}." + traceback.format_exc(),
        )


@router.delete(
    "/student-info/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Users - Student Info"],
)
async def delete_student_info(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        await svc.delete_student_info_by_user_id(user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to delete student info: {e}." + traceback.format_exc(),
        )


@router.post(
    "/preferences",
    response_model=IDResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users - Preferences"],
)
async def create_preferences(
    payload: UserPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        return await svc.create_user_preferences(payload)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to create preferences: {e}." + traceback.format_exc(),
        )


@router.get(
    "/preferences", response_model=UserPreferenceResponse, tags=["Users - Preferences"]
)
async def get_preferences(
    user_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        return await svc.get_preferences(current_user, user_id)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to retrieve preferences: {e}." + traceback.format_exc(),
        )


@router.put(
    "/preferences", response_model=UserPreferenceResponse, tags=["Users - Preferences"]
)
async def update_preferences(
    payload: UserPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        return await svc.update_preferences(current_user, payload)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to update preferences: {e}." + traceback.format_exc(),
        )


@router.delete(
    "/preferences", status_code=status.HTTP_204_NO_CONTENT, tags=["Users - Preferences"]
)
async def delete_preferences(
    user_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = UserService(db)
        await svc.delete_preferences(current_user, user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to delete preferences: {e}." + traceback.format_exc(),
        )

import logging
import traceback
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.exc import LoggedHTTPException, raise_with_log
from app.models.users import User
from app.schemas.operating_systems import (
    OSBaseCreateRequest,
    OSResponse,
    OSUpdateRequest,
)
from app.services.operating_systems import OSService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/os", tags=["Operating Systems"])


@router.get("/", response_model=list[OSResponse])
async def list_os(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return await OSService(db).list_os()
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to list OS: {e}." + traceback.format_exc(),
        )


@router.get("/{os_id}", response_model=OSResponse)
async def get_os(
    os_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return await OSService(db).get_os(os_id)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to retrieve OS: {e}." + traceback.format_exc(),
        )


@router.post(
    "/",
    response_model=OSResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_os(
    payload: OSBaseCreateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return await OSService(db).create_os(payload)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to create OS: {e}." + traceback.format_exc(),
        )


@router.put("/{os_id}", response_model=OSResponse)
async def update_os(
    os_id: UUID,
    payload: OSUpdateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return await OSService(db).update_os(os_id, payload)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to update OS: {e}." + traceback.format_exc(),
        )


@router.delete("/{os_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_os(
    os_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        await OSService(db).delete_os(os_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to delete OS: {e}." + traceback.format_exc(),
        )

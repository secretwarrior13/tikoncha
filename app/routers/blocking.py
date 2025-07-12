# app/api/endpoints/blocking/router.py
import traceback
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.blocking import (
    BlockingStatusResponse,
    EmergencyExceptionResponse,
    SchoolScheduleResponse,
    EmergencyExceptionRequest,
    BlockedAppListItem,
)
from app.services.blocking import BlockingServiceAsync
from app.models.user import User

router = APIRouter(prefix="/blocking", tags=["Blocking"])


@router.get(
    "/status",
    response_model=BlockingStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await BlockingServiceAsync(db).get_status(current_user)
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error",
        )


@router.get(
    "/blocked-apps",
    response_model=List[BlockedAppListItem],
    status_code=status.HTTP_200_OK,
)
async def list_blocked_apps(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await BlockingServiceAsync(db).list_blocked_apps(current_user)
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error",
        )


@router.post(
    "/emergency-exceptions",
    response_model=EmergencyExceptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def emergency_exception(
    payload: EmergencyExceptionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await BlockingServiceAsync(db).request_exception(
            user=current_user,
            app_id=payload.app_id,
            reason=payload.reason,
        )
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error",
        )


@router.get(
    "/school-schedule",
    response_model=SchoolScheduleResponse,
    status_code=status.HTTP_200_OK,
)
async def school_schedule(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await BlockingServiceAsync(db).get_schedule(
            user=current_user,
            month=month,
            year=year,
        )
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error",
        )

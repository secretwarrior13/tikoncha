<<<<<<< HEAD
import logging
import traceback
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
=======
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
<<<<<<< HEAD
from app.exc import LoggedHTTPException, raise_with_log
from app.schemas.schools import SchoolCreate, SchoolListResponse, SchoolResponse
from app.services.schools import SchoolService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
=======
from app.schemas.schools import (
    CityResponse,
    DistrictResponse,
    RegionResponse,
    SchoolCreate,
    SchoolResponse,
)
from app.services.schools import SchoolService as svc_cls
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0

router = APIRouter(prefix="/schools", tags=["Schools"])


@router.get("/", response_model=List[SchoolListResponse])
async def list_schools(
    region_id: Optional[UUID] = None,
    district_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        svc = SchoolService(db)
        return await svc.get_schools(region_id, district_id)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list schools: %s", e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not retrieve schools: {e}. {traceback.format_exc()}",
        )


@router.get("/{school_id}", response_model=SchoolResponse)
async def retrieve_school(
    school_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        svc = SchoolService(db)
        return await svc.get_school(school_id)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve school %s: %s", school_id, e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not retrieve school {school_id}: {e}. {traceback.format_exc()}",
        )


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_school(
    school: SchoolCreate,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        svc = SchoolService(db)
        return await svc.create_school(school)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create school: %s", e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not create school: {e}. {traceback.format_exc()}",
        )


@router.put(
    "/{school_id}",
    response_model=SchoolResponse,
    status_code=status.HTTP_200_OK,
)
async def update_school(
    school_id: UUID,
    data: SchoolCreate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        svc = SchoolService(db)
        return await svc.update_school(school_id, data, current_user)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update school %s: %s", school_id, e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not update school {school_id}: {e}. {traceback.format_exc()}",
        )


@router.delete(
    "/{school_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_school(
    school_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        svc = SchoolService(db)
        await svc.delete_school(school_id, current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete school %s: %s", school_id, e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not delete school {school_id}: {e}. {traceback.format_exc()}",
        )

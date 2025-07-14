import logging
import traceback
from typing import Any, Dict, List, Optional
from uuid import UUID

<<<<<<< HEAD
from fastapi import APIRouter, Depends, Query, Response, status
=======
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, status
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
<<<<<<< HEAD
from app.exc import LoggedHTTPException, raise_with_log
from app.models.users import User
from app.schemas.locations import (
    DistrictCreateRequest,
    DistrictCreateResponse,
    RegionCreateRequest,
    RegionCreateResponse,
)
from app.services.locations import LocationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/locations")


@router.get(
    "/regions", response_model=List[RegionCreateResponse], tags=["Locations - Regions"]
=======
from app.models.user import User
from app.schemas.locations import CityResponse, DistrictResponse, RegionResponse
from app.services.locations import (
    create_city,
    create_district,
    create_region,
    get_cities,
    get_districts,
    get_location_statistics,
    get_region_detail,
    get_regions,
    search_locations,
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0
)
async def get_regions(
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = LocationService(db)
        return await svc.get_regions()
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list regions: %s", e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not retrieve regions: {e}. {traceback.format_exc()}",
        )


@router.get(
    "/regions/{region_id}",
    response_model=RegionCreateResponse,
    tags=["Locations - Regions"],
)
async def get_region_detail(
    region_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        svc = LocationService(db)
        return await svc.get_region_detail(region_id, current_user)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve region %s: %s", region_id, e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not retrieve region {region_id}: {e}. {traceback.format_exc()}",
        )


@router.put(
    "/regions/{region_id}",
    response_model=RegionCreateResponse,
    status_code=status.HTTP_200_OK,
    tags=["Locations - Regions"],
)
async def update_region(
    region_id: UUID,
    region_in: RegionCreateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        svc = LocationService(db)
        return await svc.update_region(current_user, region_id, region_in)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update region %s: %s", region_id, e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not update region {region_id}: {e}. {traceback.format_exc()}",
        )


@router.delete(
    "/regions/{region_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Locations - Regions"],
)
async def delete_region(
    region_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        svc = LocationService(db)
        await svc.delete_region(current_user, region_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete region %s: %s", region_id, e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not delete region {region_id}: {e}. {traceback.format_exc()}",
        )


@router.get(
    "/districts",
    response_model=List[DistrictCreateResponse],
    tags=["Locations - Districts"],
)
async def get_districts(
    region_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = LocationService(db)
        return await svc.get_districts(region_id)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list districts: %s", e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not retrieve districts: {e}. {traceback.format_exc()}",
        )


@router.post(
    "/regions",
    response_model=RegionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Locations - Regions"],
)
async def add_region(
    region_in: RegionCreateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        svc = LocationService(db)
        return await svc.create_region(current_user, region_in)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create region: %s", e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not create region: {e}. {traceback.format_exc()}",
        )


@router.post(
    "/districts",
    response_model=DistrictCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Locations - Districts"],
)
async def add_district(
    district_in: DistrictCreateRequest,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        svc = LocationService(db)
        return await svc.create_district(district_in)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create district: %s", e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not create district: {e}. {traceback.format_exc()}",
        )


@router.get(
    "/districts/{district_id}",
    response_model=DistrictCreateResponse,
    status_code=status.HTTP_200_OK,
    tags=["Locations - Districts"],
)
async def get_district_detail(
    district_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        svc = LocationService(db)
        return await svc.get_district_detail(district_id, current_user)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve district %s: %s", district_id, e, exc_info=True
        )
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not retrieve district {district_id}: {e}. {traceback.format_exc()}",
        )


@router.put(
    "/districts/{district_id}",
    response_model=DistrictCreateResponse,
    status_code=status.HTTP_200_OK,
    tags=["Locations - Districts"],
)
async def update_district(
    district_id: UUID,
    district_in: DistrictCreateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        svc = LocationService(db)
        return await svc.update_district(current_user, district_id, district_in)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update district %s: %s", district_id, e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not update district {district_id}: {e}. {traceback.format_exc()}",
        )


@router.delete(
    "/districts/{district_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Locations - Districts"],
)
async def delete_district(
    district_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        svc = LocationService(db)
        await svc.delete_district(current_user, district_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete district %s: %s", district_id, e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not delete district {district_id}: {e}. {traceback.format_exc()}",
        )


@router.get(
    "/statistics/locations", response_model=Dict[str, Any], tags=["Locations - General"]
)
async def location_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        svc = LocationService(db)
        return await svc.get_location_statistics(current_user)
    except LoggedHTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch location statistics: %s", e, exc_info=True)
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Could not retrieve location statistics: {e}. {traceback.format_exc()}",
        )

# app/routers/location.py

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.locations import (
    RegionResponse,
    CityResponse,
    DistrictResponse,
)
from app.services.locations import (
    get_regions,
    get_region_detail,
    get_cities,
    get_districts,
    create_region,
    create_city,
    create_district,
    search_locations,
    get_location_statistics,
)

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("/regions", response_model=List[RegionResponse])
async def read_regions(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await get_regions(db, current_user)


@router.get("/regions/{region_id}", response_model=RegionResponse)
async def read_region_detail(
    region_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await get_region_detail(db, region_id, current_user)


@router.get("/cities", response_model=List[CityResponse])
async def read_cities(
    region_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await get_cities(db, current_user, region_id)


@router.get("/districts", response_model=List[DistrictResponse])
async def read_districts(
    region_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await get_districts(db, current_user, region_id)


@router.post(
    "/regions", response_model=RegionResponse, status_code=status.HTTP_201_CREATED
)
async def add_region(
    region_in: RegionResponse,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await create_region(db, current_user, region_in)


@router.post(
    "/cities", response_model=CityResponse, status_code=status.HTTP_201_CREATED
)
async def add_city(
    city_in: CityResponse,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await create_city(db, current_user, city_in)


@router.post(
    "/districts", response_model=DistrictResponse, status_code=status.HTTP_201_CREATED
)
async def add_district(
    district_in: DistrictResponse,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await create_district(db, current_user, district_in)


@router.get("/search/locations", response_model=Dict[str, Any])
async def find_locations(
    query: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await search_locations(db, current_user, query)


@router.get("/statistics/locations", response_model=Dict[str, Any])
async def location_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await get_location_statistics(db, current_user)

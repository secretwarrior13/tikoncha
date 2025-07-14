from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.schemas.schools import (
    CityResponse,
    DistrictResponse,
    RegionResponse,
    SchoolCreate,
    SchoolResponse,
)
from app.services.schools import SchoolService as svc_cls

router = APIRouter(prefix="/schools", tags=["Schools"])


@router.get("/", response_model=List[SchoolResponse])
async def list_schools(
    region_id: Optional[int] = None,
    city_id: Optional[int] = None,
    district_id: Optional[int] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = svc_cls(db)
    return await svc.get_schools(region_id, city_id, district_id)


@router.get("/{school_id}", response_model=SchoolResponse)
async def retrieve_school(
    school_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = svc_cls(db)
    return await svc.get_school(school_id)


@router.get("/regions", response_model=List[RegionResponse])
async def list_regions(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = svc_cls(db)
    return await svc.get_regions()


@router.get("/cities", response_model=List[CityResponse])
async def list_cities(
    region_id: Optional[int] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = svc_cls(db)
    return await svc.get_cities(region_id)


@router.get("/districts", response_model=List[DistrictResponse])
async def list_districts(
    city_id: Optional[int] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = svc_cls(db)
    return await svc.get_districts(city_id)


@router.post("/", response_model=Dict[str, Any], status_code=201)
async def create_school(
    school: SchoolCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    svc = svc_cls(db)
    return await svc.create_school(school, current_user)

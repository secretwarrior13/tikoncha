from typing import List, Dict, Any, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.models.user import Region, City, District
from app.schemas.locations import (
    RegionResponse,
    CityResponse,
    DistrictResponse,
)


async def get_regions(db: AsyncSession, current_user: User) -> List[Region]:
    q = await db.execute(select(Region))
    return q.scalars().all()


async def get_region_detail(
    db: AsyncSession, region_id: int, current_user: User
) -> Region:
    region = await db.get(Region, region_id)
    if not region:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Region not found")
    return region


async def get_cities(
    db: AsyncSession, current_user: User, region_id: Optional[int] = None
) -> List[City]:
    stmt = select(City)
    if region_id is not None:
        stmt = stmt.where(City.parent_region == region_id)
    q = await db.execute(stmt)
    return q.scalars().all()


async def get_districts(
    db: AsyncSession, current_user: User, region_id: Optional[int] = None
) -> List[District]:
    stmt = select(District)
    if region_id is not None:
        stmt = stmt.where(District.parent_region == region_id)
    q = await db.execute(stmt)
    return q.scalars().all()


async def create_region(
    db: AsyncSession, current_user: User, data: RegionResponse
) -> Region:
    if current_user.user_type_rel.name != "admin":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Only administrators can create regions"
        )

    exists = await db.execute(select(Region).where(Region.name == data.name))
    if exists.scalars().first():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Region with this name already exists"
        )

    new = Region(**data.dict())
    db.add(new)
    await db.flush()
    return new


async def create_city(db: AsyncSession, current_user: User, data: CityResponse) -> City:
    if current_user.user_type_rel.name != "admin":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Only administrators can create cities"
        )

    parent = await db.get(Region, data.parent_region)
    if not parent:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parent region not found")

    exists = await db.execute(select(City).where(City.name == data.name))
    if exists.scalars().first():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "City with this name already exists"
        )

    new = City(**data.dict())
    db.add(new)
    await db.flush()
    return new


async def create_district(
    db: AsyncSession, current_user: User, data: DistrictResponse
) -> District:
    if current_user.user_type_rel.name != "admin":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Only administrators can create districts"
        )

    parent = await db.get(Region, data.parent_region)
    if not parent:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parent region not found")

    exists = await db.execute(select(District).where(District.name == data.name))
    if exists.scalars().first():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "District with this name already exists"
        )

    new = District(**data.dict())
    db.add(new)
    await db.flush()
    return new


async def search_locations(
    db: AsyncSession, current_user: User, q: str
) -> Dict[str, Any]:
    if len(q) < 2:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Search query must be at least 2 characters"
        )

    regs = (
        (await db.execute(select(Region).where(Region.name.ilike(f"%{q}%"))))
        .scalars()
        .all()
    )
    cits = (
        (await db.execute(select(City).where(City.name.ilike(f"%{q}%"))))
        .scalars()
        .all()
    )
    dists = (
        (await db.execute(select(District).where(District.name.ilike(f"%{q}%"))))
        .scalars()
        .all()
    )

    return {
        "regions": [RegionResponse.from_orm(r) for r in regs],
        "cities": [CityResponse.from_orm(c) for c in cits],
        "districts": [DistrictResponse.from_orm(d) for d in dists],
    }


async def get_location_statistics(
    db: AsyncSession, current_user: User
) -> Dict[str, Any]:
    if current_user.user_type_rel.name != "admin":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Only administrators can access location statistics",
        )

    total_regions = await db.scalar(select(func.count(Region.id)))
    total_cities = await db.scalar(select(func.count(City.id)))
    total_districts = await db.scalar(select(func.count(District.id)))

    all_regs = (await db.execute(select(Region))).scalars().all()
    stats = []
    for r in all_regs:
        ccount = len(r.cities)
        dcount = len(r.districts)
        stats.append(
            {
                "id": r.id,
                "name": r.name,
                "city_count": ccount,
                "district_count": dcount,
                "total_count": ccount + dcount,
            }
        )
    stats.sort(key=lambda x: x["total_count"], reverse=True)

    return {
        "total_regions": total_regions,
        "total_cities": total_cities,
        "total_districts": total_districts,
        "regions_by_location_count": stats[:5],
    }

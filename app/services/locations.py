from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import District, Region, User
from app.schemas.locations import (
    DistrictCreateRequest,
    DistrictCreateResponse,
    RegionCreateRequest,
    RegionCreateResponse,
)


class LocationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_regions(self) -> List[Region]:
        try:
            result = await self.db.execute(select(Region))
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error fetching regions: {e}"
            )

    async def get_region_detail(
        self,
        region_id: UUID,
        current_user: User,
    ) -> Region:
        try:
            region = await self.db.get(Region, region_id)
            if not region:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Region not found")
            return region
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error retrieving region {region_id}: {e}",
            )

    async def get_districts(
        self,
        region_id: Optional[UUID] = None,
    ) -> List[DistrictCreateResponse]:
        try:
            stmt = select(District).options(selectinload(District.region))
            if region_id is not None:
                stmt = stmt.where(District.parent_region == region_id)

            result = await self.db.execute(stmt)
            districts = result.scalars().all()

            return [
                DistrictCreateResponse(
                    id=d.id,
                    name=d.name,
                    coordinate=d.coordinate,
                    parent_region=d.parent_region,
                    parent_region_name=d.region.name,
                )
                for d in districts
            ]
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error fetching districts: {e}"
            )

    async def create_region(
        self,
        current_user: User,
        data: RegionCreateRequest,
    ) -> RegionCreateResponse:
        try:
            existing = await self.db.execute(
                select(Region).where(Region.name == data.name)
            )
            if existing.scalars().first():
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Region with this name already exists"
                )

            new_region = Region(name=data.name, coordinate=data.coordinate)
            self.db.add(new_region)
            try:
                await self.db.commit()
                await self.db.refresh(new_region)
            except IntegrityError:
                await self.db.rollback()
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Region with this name already exists"
                )

            return RegionCreateResponse.from_orm(new_region)
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error creating region: {e}"
            )

    async def create_district(
        self,
        data: DistrictCreateRequest,
    ) -> DistrictCreateResponse:
        try:
            parent = await self.db.get(Region, data.parent_region)
            if not parent:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, "Parent region not found"
                )

            existing = await self.db.execute(
                select(District).where(District.name == data.name)
            )
            if existing.scalars().first():
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "District with this name already exists",
                )

            new_district = District(
                name=data.name,
                coordinate=data.coordinate,
                parent_region=data.parent_region,
            )
            self.db.add(new_district)
            try:
                await self.db.commit()
                await self.db.refresh(new_district)
            except IntegrityError:
                await self.db.rollback()
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "District with this name already exists",
                )

            return DistrictCreateResponse(
                id=new_district.id,
                name=new_district.name,
                coordinate=new_district.coordinate,
                parent_region=new_district.parent_region,
                parent_region_name=parent.name,
            )
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error creating district: {e}"
            )

    async def get_district_detail(
        self,
        district_id: UUID,
        current_user: User,
    ) -> DistrictCreateResponse:
        district = await self.db.get(District, district_id)
        if not district:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="District not found"
            )

        region = await self.db.get(Region, district.parent_region)

        return DistrictCreateResponse(
            id=district.id,
            name=district.name,
            coordinate=district.coordinate,
            parent_region=district.parent_region,
            parent_region_name=region.name if region else None,
        )

    async def get_location_statistics(
        self,
        current_user: User,
    ) -> Dict[str, Any]:
        try:
            total_regions = await self.db.scalar(select(func.count(Region.id)))
            total_districts = await self.db.scalar(select(func.count(District.id)))

            result = await self.db.execute(
                select(Region).options(selectinload(Region.districts))
            )
            regions = result.scalars().all()

            stats = [
                {
                    "id": r.id,
                    "name": r.name,
                    "district_count": len(r.districts),
                }
                for r in regions
            ]
            stats.sort(key=lambda x: x["district_count"], reverse=True)

            return {
                "total_regions": total_regions,
                "total_districts": total_districts,
                "regions_by_location_count": stats[:5],
            }
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Error fetching location statistics: {e}",
            )

    async def update_region(
        self,
        current_user: User,
        region_id: UUID,
        data: RegionCreateRequest,
    ) -> RegionCreateResponse:
        region = await self.db.get(Region, region_id)
        if not region:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Region not found")

        patch = data.model_dump(exclude_unset=True)
        if "name" in patch and patch["name"] != region.name:
            dup = await self.db.execute(
                select(Region).where(Region.name == patch["name"])
            )
            if dup.scalars().first():
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Region name already in use"
                )

        for k, v in patch.items():
            setattr(region, k, v)

        self.db.add(region)
        try:
            await self.db.commit()
            await self.db.refresh(region)
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Failed to update region (duplicate?)"
            )

        return RegionCreateResponse.from_orm(region)

    async def delete_region(
        self,
        current_user: User,
        region_id: UUID,
    ) -> None:
        region = await self.db.get(Region, region_id)
        if not region:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Region not found")

        await self.db.delete(region)
        await self.db.commit()

    async def update_district(
        self,
        current_user: User,
        district_id: UUID,
        data: DistrictCreateRequest,
    ) -> DistrictCreateResponse:

        district = await self.db.get(District, district_id)
        if not district:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "District not found")

        patch = data.model_dump(exclude_unset=True)
        if "parent_region" in patch:
            parent = await self.db.get(Region, patch["parent_region"])
            if not parent:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, "New parent region not found"
                )

        if "name" in patch and patch["name"] != district.name:
            dup = await self.db.execute(
                select(District).where(District.name == patch["name"])
            )
            if dup.scalars().first():
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "District name already in use"
                )

        for k, v in patch.items():
            setattr(district, k, v)

        self.db.add(district)
        try:
            await self.db.commit()
            await self.db.refresh(district)
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Failed to update district (duplicate?)"
            )

        parent = await self.db.get(Region, district.parent_region)
        return DistrictCreateResponse(
            id=district.id,
            name=district.name,
            coordinate=district.coordinate,
            parent_region=district.parent_region,
            parent_region_name=parent.name if parent else None,
        )

    async def delete_district(
        self,
        current_user: User,
        district_id: UUID,
    ) -> None:

        district = await self.db.get(District, district_id)
        if not district:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "District not found")

        await self.db.delete(district)
        await self.db.commit()

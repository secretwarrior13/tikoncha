# app/schools/service.py
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import City, District, Region, School, UserType
from app.schemas.schools import SchoolCreate


class SchoolService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _ensure_admin(self, user):
        ut = await self.db.get(UserType, user.user_type_id)
        if not ut or ut.name != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only admins.",
            )
        return True

    async def get_schools(
        self,
        region_id: Optional[int],
        city_id: Optional[int],
        district_id: Optional[int],
    ) -> List[Dict[str, Any]]:
        q = select(School)
        if region_id:
            q = q.filter(School.region_id == region_id)
        if city_id:
            q = q.filter(School.city_id == city_id)
        if district_id:
            q = q.filter(School.district_id == district_id)

        schools = (await self.db.execute(q)).scalars().all()
        result = []
        for s in schools:
            r = await self.db.get(Region, s.region_id)
            c = await self.db.get(City, s.city_id)
            d = await self.db.get(District, s.district_id)
            result.append(
                {
                    "id": s.id,
                    "name": s.name,
                    "address": s.address,
                    "region_id": s.region_id,
                    "region_name": r.name if r else None,
                    "city_id": s.city_id,
                    "city_name": c.name if c else None,
                    "district_id": s.district_id,
                    "district_name": d.name if d else None,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                }
            )
        return result

    async def get_school(self, school_id: int) -> Dict[str, Any]:
        s = await self.db.get(School, school_id)
        if not s:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="School not found"
            )
        r = await self.db.get(Region, s.region_id)
        c = await self.db.get(City, s.city_id)
        d = await self.db.get(District, s.district_id)
        return {
            "id": s.id,
            "name": s.name,
            "address": s.address,
            "region_id": s.region_id,
            "region_name": r.name if r else None,
            "city_id": s.city_id,
            "city_name": c.name if c else None,
            "district_id": s.district_id,
            "district_name": d.name if d else None,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }

    async def get_regions(self) -> List[Dict[str, Any]]:
        regs = (await self.db.execute(select(Region))).scalars().all()
        return [{"id": r.id, "name": r.name} for r in regs]

    async def get_cities(self, region_id: Optional[int]) -> List[Dict[str, Any]]:
        q = select(City)
        if region_id:
            q = q.filter(City.region_id == region_id)
        cities = (await self.db.execute(q)).scalars().all()
        return [{"id": c.id, "name": c.name, "region_id": c.region_id} for c in cities]

    async def get_districts(self, city_id: Optional[int]) -> List[Dict[str, Any]]:
        q = select(District)
        if city_id:
            q = q.filter(District.city_id == city_id)
        ds = (await self.db.execute(q)).scalars().all()
        return [{"id": d.id, "name": d.name, "city_id": d.city_id} for d in ds]

    async def create_school(self, data: SchoolCreate, user) -> Dict[str, Any]:
        await self._ensure_admin(user)
        # validate foreign keys
        for model, key, val in (
            (Region, "region", data.region_id),
            (City, "city", data.city_id),
            (District, "district", data.district_id),
        ):
            if not await self.db.get(model, val):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{model.__name__} {key} not found",
                )

        new = School(**data.model_dump())
        self.db.add(new)
        await self.db.commit()
        await self.db.refresh(new)
        return {
            "id": new.id,
            "name": new.name,
            "address": new.address,
            "region_id": new.region_id,
            "city_id": new.city_id,
            "district_id": new.district_id,
            "created_at": new.created_at,
        }

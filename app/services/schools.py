# app/schools/service.py
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import District, Region, School, UserRole
from app.schemas.schools import SchoolCreate


class SchoolService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _ensure_admin(self, user):
        ut = await self.db.get(UserRole, user.user_type_id)
        if not ut or ut.name != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only admins.",
            )
        return True

    async def get_schools(
        self,
        region_id: Optional[UUID],
        district_id: Optional[UUID],
    ) -> List[Dict[str, Any]]:
        q = select(School)
        if region_id:
            q = q.filter(School.region_id == region_id)
        if district_id:
            q = q.filter(School.district_id == district_id)

        schools = (await self.db.execute(q)).scalars().all()
        result = []
        for s in schools:
            r = await self.db.get(Region, s.region_id)
            d = await self.db.get(District, s.district_id)
            result.append(
                {
                    "id": s.id,
                    "name": s.name,
                    "address": s.address,
                    "region_id": s.region_id,
                    "region_name": r.name if r else None,
                    "district_id": s.district_id,
                    "district_name": d.name if d else None,
                    "created_at": s.created_at,
                }
            )
        return result

    async def get_school(self, school_id: UUID) -> Dict[str, Any]:
        s = await self.db.get(School, school_id)
        if not s:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="School not found"
            )
        r = await self.db.get(Region, s.region_id)
        d = await self.db.get(District, s.district_id)
        return {
            "id": s.id,
            "name": s.name,
            "address": s.address,
            "region_id": s.region_id,
            "region_name": r.name if r else None,
            "district_id": s.district_id,
            "district_name": d.name if d else None,
            "created_at": s.created_at,
        }

    async def create_school(
        self,
        data: SchoolCreate,
    ) -> Dict[str, Any]:
        for model, key, val in (
            (Region, "region_id", data.region_id),
            (District, "region_id", data.district_id),
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
            "district_id": new.district_id,
            "created_at": new.created_at,
        }

    async def update_school(
        self, school_id: UUID, data: SchoolCreate, current_user
    ) -> Dict[str, Any]:
        s = await self.db.get(School, school_id)
        if not s:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "School not found")

        if data.region_id and not await self.db.get(Region, data.region_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Region not found")
        if data.district_id and not await self.db.get(District, data.district_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "District not found")

        for field, val in data.model_dump(exclude_unset=True).items():
            setattr(s, field, val)

        self.db.add(s)
        await self.db.commit()
        await self.db.refresh(s)

        r = await self.db.get(Region, s.region_id)
        d = await self.db.get(District, s.district_id)
        return {
            "id": s.id,
            "name": s.name,
            "address": s.address,
            "region_id": s.region_id,
            "region_name": r.name if r else None,
            "district_id": s.district_id,
            "district_name": d.name if d else None,
            "created_at": s.created_at,
        }

    async def delete_school(self, school_id: UUID, current_user) -> None:
        s = await self.db.get(School, school_id)
        if not s:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "School not found")

        await self.db.delete(s)
        await self.db.commit()

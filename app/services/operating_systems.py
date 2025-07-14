import logging
import traceback
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.devices import OS
from app.schemas.operating_systems import (
    OSBaseCreateRequest,
    OSResponse,
    OSUpdateRequest,
)

logger = logging.getLogger(__name__)


class OSService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get(self, os_id: UUID) -> OS:
        stmt = select(OS).where(OS.id == os_id)
        result = await self.db.execute(stmt)
        os_row = result.scalars().first()
        if not os_row:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Operating-system {os_id} not found",
            )
        return os_row

    async def list_os(self) -> list[OSResponse]:
        stmt = select(OS)
        result = await self.db.execute(stmt)
        return [OSResponse.from_orm(row) for row in result.scalars().all()]

    async def get_os(self, os_id: UUID) -> OSResponse:
        return OSResponse.from_orm(await self._get(os_id))

    async def create_os(self, data: OSBaseCreateRequest) -> OSResponse:
        new_os = OS(**data.dict())
        self.db.add(new_os)
        try:
            await self.db.commit()
            await self.db.refresh(new_os)
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Duplicate operating-system entry",
            )
        return OSResponse.from_orm(new_os)

    async def update_os(self, os_id: UUID, data: OSUpdateRequest) -> OSResponse:
        os_row = await self._get(os_id)
        updates = data.dict(exclude_unset=True)
        if not updates:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "No fields supplied for update",
            )

        for k, v in updates.items():
            setattr(os_row, k, v)

        self.db.add(os_row)
        await self.db.commit()
        await self.db.refresh(os_row)
        return OSResponse.from_orm(os_row)

    async def delete_os(self, os_id: UUID) -> None:
        os_row = await self._get(os_id)
        await self.db.delete(os_row)
        await self.db.commit()

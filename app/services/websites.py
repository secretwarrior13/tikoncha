from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Website, Policy
from app.schemas.websites import WebsiteCreate, PolicyCreate


class WebsiteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_websites(
        self, general_type: Optional[str] = None, priority: Optional[str] = None
    ) -> List[Website]:
        stmt = select(Website)
        if general_type:
            stmt = stmt.where(Website.general_type == general_type)
        if priority:
            stmt = stmt.where(Website.priority == priority)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_website(self, website_id: int) -> Website:
        stmt = select(Website).where(Website.id == website_id)
        result = await self.db.execute(stmt)
        website = result.scalars().first()
        if not website:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Website not found"
            )
        return website

    async def create_website(self, data: WebsiteCreate, is_admin: bool) -> Website:
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create websites.",
            )

        # ensure no duplicates
        dup = (
            (await self.db.execute(select(Website).where(Website.url == data.url)))
            .scalars()
            .first()
        )
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Website with this URL already exists",
            )

        website = Website(**data.model_dump())
        self.db.add(website)
        try:
            await self.db.commit()
            await self.db.refresh(website)
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create website",
            )
        return website


class PolicyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_policies(self) -> List[Policy]:
        result = await self.db.execute(select(Policy))
        return result.scalars().all()

    async def get_policy(self, policy_id: int) -> Policy:
        result = await self.db.execute(select(Policy).where(Policy.id == policy_id))
        policy = result.scalars().first()
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found"
            )
        return policy

    async def create_policy(self, data: PolicyCreate, is_admin: bool) -> Policy:
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create policies.",
            )

        policy = Policy(**data.model_dump())
        self.db.add(policy)
        try:
            await self.db.commit()
            await self.db.refresh(policy)
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create policy",
            )
        return policy

    async def get_latest_policy(self) -> Policy:
        result = await self.db.execute(
            select(Policy).order_by(Policy.created_at.desc()).limit(1)
        )
        policy = result.scalars().first()
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No policies found"
            )
        return policy

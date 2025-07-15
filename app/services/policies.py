from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Policy
from app.schemas.policies import PolicyCreateRequest, PolicyUpdateRequest


class PolicyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_policies(self) -> List[Policy]:
        statement = select(Policy)
        result = await self.db.exec(statement)
        return result.all()

    async def get_policy(self, policy_id: UUID) -> Policy:
        policy = await self.db.get(Policy, policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        return policy

    async def create_policy(self, payload: PolicyCreateRequest) -> Policy:
        new_policy = Policy.from_orm(payload)
        self.db.add(new_policy)
        await self.db.commit()
        await self.db.refresh(new_policy)
        return new_policy

    async def update_policy(
        self, policy_id: UUID, payload: PolicyUpdateRequest
    ) -> Policy:
        policy = await self.get_policy(policy_id)
        update_data = payload.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def delete_policy(self, policy_id: UUID) -> None:
        policy = await self.get_policy(policy_id)
        await self.db.delete(policy)
        await self.db.commit()

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.models import Policy
from app.models.users import User
from app.schemas.policies import PolicyCreateRequest, PolicyRead, PolicyUpdateRequest
from app.services.policies import PolicyService

router = APIRouter(prefix="/policies", tags=["Policies"])


def get_policy_service(
    db: AsyncSession = Depends(get_async_session),
) -> PolicyService:
    return PolicyService(db)


@router.get(
    "/",
    response_model=List[PolicyRead],
)
async def list_policies(
    service: PolicyService = Depends(get_policy_service),
    current_user: User = Depends(get_current_user),
) -> List[Policy]:
    return await service.list_policies()


@router.get(
    "/{policy_id}",
    response_model=PolicyRead,
)
async def get_policy(
    policy_id: UUID,
    service: PolicyService = Depends(get_policy_service),
    current_user: User = Depends(get_current_user),
) -> Policy:
    policy = await service.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.post(
    "/",
    response_model=PolicyRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_policy(
    payload: PolicyCreateRequest,
    service: PolicyService = Depends(get_policy_service),
    current_user: User = Depends(get_current_user),
) -> Policy:
    return await service.create_policy(payload)


@router.patch(
    "/{policy_id}",
    response_model=PolicyRead,
)
async def update_policy(
    policy_id: UUID,
    payload: PolicyUpdateRequest,
    service: PolicyService = Depends(get_policy_service),
    current_user: User = Depends(get_current_user),
) -> Policy:
    updated = await service.update_policy(policy_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Policy not found")
    return updated


@router.delete(
    "/{policy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_policy(
    policy_id: UUID,
    service: PolicyService = Depends(get_policy_service),
    current_user: User = Depends(get_current_user),
):
    await service.delete_policy(policy_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

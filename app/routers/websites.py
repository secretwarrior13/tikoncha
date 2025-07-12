from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.websites import (
    WebsiteCreate,
    WebsiteResponse,
    PolicyCreate,
    PolicyResponse,
)
from app.services.websites import WebsiteService, PolicyService
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/websites",
    tags=["Websites"],
)


@router.get("/", response_model=List[WebsiteResponse])
async def get_websites(
    general_type: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = WebsiteService(db)
    websites = await svc.list_websites(general_type, priority)
    return [WebsiteResponse.model_validate(w) for w in websites]


@router.get("/{website_id}", response_model=WebsiteResponse)
async def get_website(
    website_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = WebsiteService(db)
    website = await svc.get_website(website_id)
    return WebsiteResponse.model_validate(website)


@router.post("/", response_model=WebsiteResponse)
async def create_website(
    data: WebsiteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = WebsiteService(db)
    is_admin = getattr(current_user.user_type, "name", "") == "admin"
    website = await svc.create_website(data, is_admin)
    return WebsiteResponse.model_validate(website)


policy_router = APIRouter(
    prefix="/policies",
    tags=["policies"],
)


@policy_router.get("/", response_model=List[PolicyResponse])
async def get_policies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = PolicyService(db)
    policies = await svc.list_policies()
    return [PolicyResponse.model_validate(p) for p in policies]


@policy_router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = PolicyService(db)
    policy = await svc.get_policy(policy_id)
    return PolicyResponse.model_validate(policy)


@policy_router.post("/", response_model=PolicyResponse)
async def create_policy(  # <- fixed )
    data: PolicyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = PolicyService(db)
    is_admin = getattr(current_user.user_type, "name", "") == "admin"
    policy = await svc.create_policy(data, is_admin)
    return PolicyResponse.model_validate(policy)


@policy_router.get("/latest", response_model=PolicyResponse)
async def get_latest_policy(  # <- fixed )
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = PolicyService(db)
    policy = await svc.get_latest_policy()
    return PolicyResponse.model_validate(policy)

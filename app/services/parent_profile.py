from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import ParentInfo, User, UserType
from app.schemas.parent_profile import (
    ChildInfo,
    ParentChildrenResponse,
    ParentProfileResponse,
    ParentProfileUpdate,
)


async def get_parent_profile(
    db: AsyncSession, current_user: User
) -> ParentProfileResponse:
    ut = (
        (
            await db.execute(
                select(UserType).where(UserType.id == current_user.user_type_id)
            )
        )
        .scalars()
        .first()
    )
    if not ut or ut.name != "parent":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only parents can view profile")

    pi = (
        (
            await db.execute(
                select(ParentInfo).where(ParentInfo.user_id == current_user.id)
            )
        )
        .scalars()
        .first()
    )
    if not pi:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parent profile not found")

    return ParentProfileResponse(
        id=pi.id,
        user_id=pi.user_id,
        gender=pi.gender,
        address=pi.address,
        created_at=pi.created_at.isoformat(),
        updated_at=pi.updated_at.isoformat(),
    )


async def update_parent_profile(
    db: AsyncSession, current_user: User, data: ParentProfileUpdate
) -> ParentProfileResponse:
    ut = (
        (
            await db.execute(
                select(UserType).where(UserType.id == current_user.user_type_id)
            )
        )
        .scalars()
        .first()
    )
    if not ut or ut.name != "parent":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Only parents can update profile"
        )

    pi = (
        (
            await db.execute(
                select(ParentInfo).where(ParentInfo.user_id == current_user.id)
            )
        )
        .scalars()
        .first()
    )
    if not pi:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parent profile not found")

    if data.gender is not None:
        pi.gender = data.gender
    if data.address is not None:
        pi.address = data.address

    await db.commit()
    await db.refresh(pi)

    return ParentProfileResponse(
        id=pi.id,
        user_id=pi.user_id,
        gender=pi.gender,
        address=pi.address,
        created_at=pi.created_at.isoformat(),
        updated_at=pi.updated_at.isoformat(),
    )


async def get_parent_children(
    db: AsyncSession, current_user: User
) -> ParentChildrenResponse:
    ut = (
        (
            await db.execute(
                select(UserType).where(UserType.id == current_user.user_type_id)
            )
        )
        .scalars()
        .first()
    )
    if not ut or ut.name != "parent":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only parents can view children")

    pi = (
        (
            await db.execute(
                select(ParentInfo).where(ParentInfo.user_id == current_user.id)
            )
        )
        .scalars()
        .first()
    )
    if not pi:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parent profile not found")

    # TODO: replace mock with real child query
    mock_children = [
        ChildInfo(id=1, name="Child 1", age=10, school="School 1"),
        ChildInfo(id=2, name="Child 2", age=8, school="School 2"),
    ]

    return ParentChildrenResponse(
        message="Children associated with this parent",
        parent_id=pi.id,
        children=mock_children,
    )

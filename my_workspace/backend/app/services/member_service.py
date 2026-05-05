from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.member_profile import MemberProfile
from app.models.user import User
from app.schemas.member import MemberProfileRead, MemberProfileUpdate, MemberProfileStaffUpdate


async def _get_or_create_profile(user_id: UUID, db: AsyncSession) -> MemberProfile:
    result = await db.execute(select(MemberProfile).where(MemberProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = MemberProfile(user_id=user_id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


def _build_response(user: User, profile: MemberProfile) -> MemberProfileRead:
    return MemberProfileRead(
        id=user.id,
        email=user.email,
        member_code=user.member_code,
        national_id=user.national_id,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        title=profile.title,
        position=profile.position,
        department=profile.department,
        organization=profile.organization,
        phone=profile.phone,
        addr_house_no=profile.addr_house_no,
        addr_moo=profile.addr_moo,
        addr_road=profile.addr_road,
        addr_tambon=profile.addr_tambon,
        addr_amphur=profile.addr_amphur,
        addr_province=profile.addr_province,
        salary=float(profile.salary) if profile.salary is not None else None,
        shares_amount=float(profile.shares_amount) if profile.shares_amount is not None else None,
        existing_debt=float(profile.existing_debt) if profile.existing_debt is not None else None,
        updated_at=profile.updated_at,
    )


async def get_profile(user_id: UUID, db: AsyncSession) -> MemberProfileRead:
    result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.profile))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("ไม่พบผู้ใช้")
    profile = await _get_or_create_profile(user_id, db)
    return _build_response(user, profile)


async def update_profile(
    user_id: UUID,
    data: MemberProfileUpdate | MemberProfileStaffUpdate,
    db: AsyncSession,
) -> MemberProfileRead:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("ไม่พบผู้ใช้")

    profile = await _get_or_create_profile(user_id, db)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return _build_response(user, profile)

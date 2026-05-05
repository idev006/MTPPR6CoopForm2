from uuid import UUID
from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.dependencies import CurrentUser, DbSession, StaffOnly
from app.models.user import User
from app.models.member_profile import MemberProfile
from app.schemas.member import MemberProfileRead, MemberProfileUpdate, MemberProfileStaffUpdate, MemberListItem
from app.services import member_service

router = APIRouter(prefix="/members", tags=["members"])


@router.get("/me/profile", response_model=MemberProfileRead)
async def get_my_profile(current_user: CurrentUser, db: DbSession):
    return await member_service.get_profile(UUID(current_user["id"]), db)


@router.put("/me/profile", response_model=MemberProfileRead)
async def update_my_profile(
    body: MemberProfileUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    return await member_service.update_profile(UUID(current_user["id"]), body, db)


@router.put("/me/profile/staff", response_model=MemberProfileRead)
async def staff_update_profile(
    body: MemberProfileStaffUpdate,
    current_user: StaffOnly,
    db: DbSession,
):
    return await member_service.update_profile(UUID(current_user["id"]), body, db)


@router.get("", response_model=List[MemberListItem])
async def list_members(current_user: StaffOnly, db: DbSession):
    result = await db.execute(
        select(User)
        .where(User.role == "borrower", User.is_active == True)
        .options(selectinload(User.profile))
        .order_by(User.first_name, User.last_name)
    )
    users = result.scalars().all()
    return [
        MemberListItem(
            id=u.id,
            email=u.email,
            member_code=u.member_code,
            first_name=u.first_name,
            last_name=u.last_name,
            salary=float(u.profile.salary) if u.profile and u.profile.salary is not None else None,
            shares_amount=float(u.profile.shares_amount) if u.profile and u.profile.shares_amount is not None else None,
            existing_debt=float(u.profile.existing_debt) if u.profile and u.profile.existing_debt is not None else None,
        )
        for u in users
    ]


@router.put("/{member_id}/financial", response_model=MemberProfileRead)
async def update_member_financial(
    member_id: UUID,
    body: MemberProfileStaffUpdate,
    current_user: StaffOnly,
    db: DbSession,
):
    result = await db.execute(select(User).where(User.id == member_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบสมาชิก")
    return await member_service.update_profile(member_id, body, db)

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MemberProfileRead(BaseModel):
    # User (read-only)
    id: UUID
    email: str
    member_code: str | None
    national_id: str | None
    first_name: str
    last_name: str
    role: str
    # Profile Type A (editable by borrower)
    title: str | None
    position: str | None
    department: str | None
    organization: str | None
    phone: str | None
    addr_house_no: str | None
    addr_moo: str | None
    addr_road: str | None
    addr_tambon: str | None
    addr_amphur: str | None
    addr_province: str | None
    # Profile Type B (staff only)
    salary: float | None
    shares_amount: float | None
    existing_debt: float | None
    updated_at: datetime | None


class MemberProfileUpdate(BaseModel):
    title: str | None = None
    position: str | None = None
    department: str | None = None
    organization: str | None = None
    phone: str | None = None
    addr_house_no: str | None = None
    addr_moo: str | None = None
    addr_road: str | None = None
    addr_tambon: str | None = None
    addr_amphur: str | None = None
    addr_province: str | None = None


class MemberProfileStaffUpdate(MemberProfileUpdate):
    salary: float | None = None
    shares_amount: float | None = None
    existing_debt: float | None = None


class MemberListItem(BaseModel):
    id: UUID
    email: str
    member_code: str | None
    first_name: str
    last_name: str
    salary: float | None
    shares_amount: float | None
    existing_debt: float | None

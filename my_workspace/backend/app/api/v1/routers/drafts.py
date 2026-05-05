from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.schemas.draft import DraftCreate, DraftRead, DraftUpdate
from app.services import draft_service

router = APIRouter(prefix="/drafts", tags=["drafts"])


@router.post("", response_model=DraftRead, status_code=200)
async def create_or_get_draft(body: DraftCreate, current_user: CurrentUser, db: DbSession):
    draft = await draft_service.get_or_create_draft(
        UUID(current_user["id"]), body.form_type, db
    )
    return draft


@router.get("/{form_type}", response_model=DraftRead)
async def get_draft(form_type: str, current_user: CurrentUser, db: DbSession):
    draft = await draft_service.get_draft_by_form_type(UUID(current_user["id"]), form_type, db)
    if not draft:
        raise NotFoundError("ไม่พบ draft สำหรับ form นี้")
    return draft


@router.put("/{draft_id}", response_model=DraftRead)
async def update_draft(draft_id: UUID, body: DraftUpdate, current_user: CurrentUser, db: DbSession):
    return await draft_service.update_draft(
        draft_id, UUID(current_user["id"]), body.model_dump(exclude_unset=True), db
    )


@router.delete("/{draft_id}", status_code=204)
async def delete_draft(draft_id: UUID, current_user: CurrentUser, db: DbSession):
    await draft_service.delete_draft(draft_id, UUID(current_user["id"]), db)

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
from uuid import UUID
from pathlib import Path

from app.core.dependencies import StaffOnly, DbSession
from app.models import LoanApplication
from app.schemas.application_review import ReviewRequest, ApplicationStaffListItem, ApplicationStaffDetail
from app.services.review_service import ReviewService
from app.core.config import settings
from sqlalchemy import select

router = APIRouter(prefix="/staff/applications", tags=["staff-applications"])


@router.get("/{app_id}/pdf")
async def get_application_pdf(
    app_id: UUID,
    current_user: StaffOnly,
    db: DbSession,
):
    stmt = select(LoanApplication).where(LoanApplication.id == app_id)
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    filename = f"{app.application_no.replace('/', '-')}.pdf"
    file_path = Path(settings.DATA_DIR) / "generated_pdfs" / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found. It might still be generating.")

    return FileResponse(path=file_path, filename=filename, media_type="application/pdf")


@router.get("", response_model=List[ApplicationStaffListItem])
async def list_applications(
    current_user: StaffOnly,
    db: DbSession,
    status: Optional[str] = Query(None, pattern="^(submitted|under_review|approved|rejected|pending_documents)$"),
):
    service = ReviewService(db)
    return await service.get_applications_for_staff(status=status)


@router.get("/{app_id}", response_model=ApplicationStaffDetail)
async def get_application(app_id: UUID, current_user: StaffOnly, db: DbSession):
    service = ReviewService(db)
    detail = await service.get_application_detail(app_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Application not found")
    return detail


@router.post("/{app_id}/review")
async def review_application(
    app_id: UUID,
    req: ReviewRequest,
    request: Request,
    current_user: StaffOnly,
    db: DbSession,
):
    service = ReviewService(db)
    try:
        app = await service.update_status(
            app_id=app_id,
            staff_user=current_user,
            req=req,
            ip=request.client.host,
        )
        return {"success": True, "status": app.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{app_id}/regenerate-pdf")
async def regenerate_application_pdf(app_id: UUID, current_user: StaffOnly, db: DbSession):
    service = ReviewService(db)
    try:
        await service.regenerate_pdf(app_id)
        return {"success": True, "message": "Re-generated PDF successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

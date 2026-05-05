from fastapi import APIRouter, HTTPException
from app.engines.form_engine import FormEngine

router = APIRouter(prefix="/forms", tags=["forms"])


@router.get("/{form_id}/config")
async def get_form_config(form_id: str):
    """Return step definitions and metadata for a given form type."""
    try:
        engine = FormEngine(form_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Form config '{form_id}' not found")

    return {
        "form_id": form_id,
        "meta": engine.get_meta(),
        "steps": engine.get_steps(),
    }

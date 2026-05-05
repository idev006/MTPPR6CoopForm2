import datetime
from pathlib import Path
from typing import Any, Dict, List

import tomli as tomllib

from loguru import logger
from app.utils.thai_baht import baht_to_text


CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "config" / "forms"


class FormEngine:
    """
    Config-driven form processor.
    Reads a TOML file → produces PDF field mappings from raw form_data.
    Supports ordinary and emergency loan form types.
    """

    def __init__(self, form_id: str):
        self.form_id = form_id
        self.config = self._load_config(form_id)

    # ── Public API ─────────────────────────────────────────

    def get_pdf_fields(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate form_data dict → {pdf_field_name: value} using TOML mapping."""
        result: Dict[str, Any] = {}
        for field_def in self.config.get("pdf_fields", []):
            try:
                key = field_def["pdf_key"]
                value = self._resolve_field(field_def, form_data)
                if value is not None:
                    result[key] = value
            except Exception as exc:
                logger.warning(f"FormEngine [{self.form_id}] field '{field_def.get('pdf_key')}': {exc}")
        return result

    def get_steps(self) -> List[Dict[str, Any]]:
        """Return step definitions for frontend consumption."""
        return self.config.get("steps", [])

    def get_meta(self) -> Dict[str, Any]:
        """Return form metadata (form_id, prefix, pdf_template, etc.)."""
        return self.config.get("meta", {})

    # ── Field resolution ───────────────────────────────────

    def _resolve_field(self, field_def: Dict[str, Any], form_data: Dict[str, Any]) -> Any:
        field_type = field_def.get("type", "direct")

        if field_type == "computed":
            return self._computed(field_def["fn"], form_data)

        if field_type == "concat":
            parts = [str(self._get_path(form_data, s) or "") for s in field_def["sources"]]
            sep = field_def.get("separator", "")
            return sep.join(p for p in parts if p)

        if field_type == "signature":
            condition_val = self._get_path(form_data, field_def["condition"])
            if not condition_val:
                return None
            return self._get_path(form_data, field_def["source"])

        # default: "direct"
        raw = self._get_path(form_data, field_def.get("source", ""))
        transform = field_def.get("transform")
        return self._apply_transform(raw, transform)

    def _computed(self, fn_name: str, form_data: Dict[str, Any]) -> Any:
        now = datetime.datetime.now()
        if fn_name == "thai_date_now":
            return self._to_thai_date(now)
        raise ValueError(f"Unknown computed fn: {fn_name}")

    def _apply_transform(self, value: Any, transform: str | None) -> Any:
        if transform is None or value is None:
            return value if value != "" else None
        if transform == "format_number":
            try:
                return "{:,.0f}".format(float(value))
            except (TypeError, ValueError):
                return str(value)
        if transform == "baht_to_text":
            try:
                return baht_to_text(float(value)) if value else None
            except Exception:
                return None
        raise ValueError(f"Unknown transform: {transform}")

    # ── Path accessor ──────────────────────────────────────

    @staticmethod
    def _get_path(data: Dict[str, Any], path: str) -> Any:
        """Access nested dict via dot-notation path, e.g. 'step1.first_name'."""
        if not path:
            return None
        parts = path.split(".")
        current: Any = data
        for part in parts:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    # ── Helpers ────────────────────────────────────────────

    @staticmethod
    def _to_thai_date(dt: datetime.datetime) -> str:
        thai_months = [
            "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
            "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
        ]
        return f"{dt.day} {thai_months[dt.month - 1]} {dt.year + 543}"

    # ── Config loader ──────────────────────────────────────

    @staticmethod
    def _load_config(form_id: str) -> Dict[str, Any]:
        path = CONFIG_DIR / f"{form_id}.toml"
        if not path.exists():
            raise FileNotFoundError(f"Form config not found: {path}")
        with open(path, "rb") as f:
            return tomllib.load(f)

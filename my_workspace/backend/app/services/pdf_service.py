import datetime
import math
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger

from app.engines import PdfEngine, FormEngine
from app.core.config import settings
from app.utils.thai_baht import baht_to_text


class PdfService:
    def __init__(self):
        self.font_path = Path(settings.ASSETS_DIR) / "font" / "THSarabunNew" / "THSarabunNew.ttf"
        self.check_icon = Path(settings.ASSETS_DIR) / "icons" / "check.png"
        self.template_dir = Path(settings.ASSETS_DIR) / "templates"
        self.output_dir = Path(settings.DATA_DIR) / "generated_pdfs"

        self.engine = PdfEngine(self.font_path, self.check_icon)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_ordinary_loan_pdf(self, form_data: Dict[str, Any], application_no: str) -> Path:
        template_path = self.template_dir / "loan_ordinary_v1.pdf"
        output_path = self.output_dir / f"{application_no.replace('/', '-')}.pdf"

        flat_data = self._map_ordinary_loan(form_data)
        success = self.engine.fill_form(template_path, output_path, flat_data)

        if not success:
            raise RuntimeError("Failed to generate PDF")
        return output_path

    def generate_preview_pdf(self, form_data: Dict[str, Any], user_id: str) -> Path:
        """สร้าง PDF ตัวอย่างชั่วคราวสำหรับผู้กู้ตรวจสอบก่อน submit."""
        preview_dir = self.output_dir.parent / "previews"
        preview_dir.mkdir(parents=True, exist_ok=True)
        output_path = preview_dir / f"{user_id}.pdf"

        if output_path.exists():
            output_path.unlink()

        template_path = self.template_dir / "loan_ordinary_v1.pdf"
        flat_data = self._map_ordinary_loan(form_data)
        success = self.engine.fill_form(template_path, output_path, flat_data)

        if not success:
            raise RuntimeError("Failed to generate preview PDF")
        return output_path

    def generate_emergency_loan_pdf(self, form_data: Dict[str, Any], application_no: str) -> Path:
        return self.fill_via_engine("loan_emergency", form_data, application_no)

    def fill_via_engine(self, form_id: str, form_data: Dict[str, Any], application_no: str) -> Path:
        """Engine-driven PDF generation — reads TOML config, maps fields, fills PDF."""
        engine = FormEngine(form_id)
        meta = engine.get_meta()
        template_path = self.template_dir / meta["pdf_template"]
        output_path = self.output_dir / f"{application_no.replace('/', '-')}.pdf"

        flat_data = engine.get_pdf_fields(form_data)
        success = self.engine.fill_form(template_path, output_path, flat_data)

        if not success:
            raise RuntimeError(f"Failed to generate PDF for {form_id}")
        return output_path

    # ─────────────────────────────────────────────────────────────────────────
    # Ordinary Loan mapping — all pages 1-5
    # ─────────────────────────────────────────────────────────────────────────

    def _map_ordinary_loan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s1 = data.get("step1", {})
        s2 = data.get("step2", {})
        s3 = data.get("step3", {})
        s4 = data.get("step4", {})
        s5 = data.get("step5", {})
        s6 = data.get("step6", {})

        now = datetime.datetime.now()
        thai_date_now = self._to_thai_date(now)

        pdf_fields: Dict[str, Any] = {}

        def sv(keys: Any, val: Any) -> None:
            if isinstance(keys, str):
                pdf_fields[keys] = val
            else:
                for k in keys:
                    pdf_fields[k] = val

        # ── Derived values ────────────────────────────────────────────────────
        fullname = f"{s1.get('title', '')}{s1.get('first_name', '')} {s1.get('last_name', '')}"
        loan_amount = s2.get("loan_amount") or 0
        repayment_period = s2.get("repayment_period") or 0
        annual_rate = settings.INTEREST_RATE_ORDINARY
        monthly_payment = self._calc_monthly_payment(loan_amount, annual_rate, repayment_period)
        amount_text = baht_to_text(loan_amount) if loan_amount else ""
        monthly_text = baht_to_text(monthly_payment) if monthly_payment else ""
        period_text_words = self._num_to_words(int(repayment_period)) + "งวด" if repayment_period else ""

        addr_current = s1.get("current_addr", {})
        addr_register = s1.get("register_addr", {})

        # effective_date from step6 (could be empty)
        effective_date_str = s6.get("effective_date", "")
        effective_date = self._parse_date(effective_date_str) if effective_date_str else now
        start_month = self._to_thai_month_year(self._add_one_month(effective_date))
        effective_date_thai = self._to_thai_date(effective_date) if effective_date_str else ""

        # ── PAGE 1 — Document checklist (step5) ───────────────────────────────
        checklist = s5.get("checklist_items", [])
        for i in range(1, 19):
            has = bool(checklist[i - 1]) if i - 1 < len(checklist) else False
            sv(f"chk_p1.doc_for_ordinary_loan.ch{i}.have", "Y" if has else "")
            sv(f"chk_p1.doc_for_ordinary_loan.ch{i}.nohave", "Y" if not has else "")

        # ── PAGE 2 — Application form ─────────────────────────────────────────
        sv("txt_p2.geninfo.write_at", s1.get("organization", ""))
        sv("txt_p2.geninfo.write_date", thai_date_now)

        # Borrower general info
        sv("txt_p2.pookoo.geninfo.fullname", fullname)
        sv("txt_p2.pookoo.geninfo.position", s1.get("position", ""))
        sv("txt_p2.pookoo.geninfo.sangud", s1.get("department", ""))
        sv("txt_p2.pookoo.geninfo.mem_id", s1.get("member_code", ""))
        sv("txt_p2.pookoo.geninfo.card_id", s1.get("id_card", ""))

        # Salary checkbox + amount
        sv("chk_p2.pookoo.geninfo.has_sarary", "Y")
        sv("txt_p2.pookoo.geninfo_sarary_amount", self._format_num(s1.get("salary")))

        # Current address (page 2)
        sv("txt_p2.pookoo.addr.house_no", addr_current.get("house_no", ""))
        sv("txt_p2.pookoo.addr.moo_no", addr_current.get("moo", ""))
        sv("txt_p2.pookoo.addr.road", addr_current.get("road", ""))
        sv("txt_p2.pookoo.addr.tambon", addr_current.get("tambon", ""))
        sv("txt_p2.pookoo.addr.amphur", addr_current.get("amphur", ""))
        sv("txt_p2.pookoo.addr.province", addr_current.get("province", ""))

        # Register address (page 2)
        sv("txt_p2.pookoo.addr2.house_no", addr_register.get("house_no", ""))
        sv("txt_p2.pookoo.addr2.moo_no", addr_register.get("moo", ""))
        sv("txt_p2.pookoo.addr2.road", addr_register.get("road", ""))
        sv("txt_p2.pookoo.addr2.tambon", addr_register.get("tambon", ""))
        sv("txt_p2.pookoo.addr2.amphur", addr_register.get("amphur", ""))
        sv("txt_p2.pookoo.addr2.province", addr_register.get("province", ""))

        # Shares amount (ทุนเรือนหุ้น)
        sv("txt_p2.pookoo.kooinfo.samun.toonreunhoon_amount", self._format_num(s1.get("shares_amount")))

        # Loan amount — numeric (appears in two spots)
        sv("txt_p2.pookoo.kooinfo.samun.amount1", self._format_num(loan_amount))
        sv("txt_p2.pookoo.kooinfo.samun.amount2", self._format_num(loan_amount))
        # Loan amount in Thai words
        sv("txt_p2.pookoo.kooinfo.samun.amount_text1", amount_text)
        sv("txt_p2.pookoo.kooinfo.samun.amount_text2", amount_text)

        # Loan type: default chk1 (ไม่มีไถ่ถอน)
        sv("chk_p2.pookoo.kooinfo.samun.chk1", "Y")
        sv("chk_p2.pookoo.kooinfo.samun.chk2", "")

        # Purpose and repayment period
        sv("txt_p2.pookoo.kooinfo.purpose", s2.get("loan_purpose", ""))
        sv("txt_p2.pookoo.kooinfo.nguad_amount", str(int(repayment_period)) if repayment_period else "")

        # Payout method
        payout = s2.get("payout_method", "transfer")
        is_transfer = payout == "transfer"
        sv("chk_p2.pookoo.kooinfo.recv.myself", "Y" if payout == "cash" else "")
        sv("chk_p2.pookoo.kooinfo.recv.by_bank", "Y" if is_transfer else "")
        sv("chk_p2.pookoo.kooinfo.recv.book_bank", "Y" if is_transfer else "")
        sv("txt_p2.pookoo.kooinfo.recv.by_bank.bank_name", s2.get("bank_name", "") if is_transfer else "")
        sv("chk_p2.pookoo.kooinfo.recv.by_bank.account_no", s2.get("bank_account_no", "") if is_transfer else "")
        sv("chk_p2.pookoo.kooinfo.recv.by_bank.account_name", s2.get("bank_account_name", "") if is_transfer else "")

        # Borrower signature (page 2)
        bsig = s4.get("borrower_sig", {})
        if bsig.get("signed"):
            sv("sign_p2.pookoo.sign", bsig.get("signature_base64"))
            sv("txt_p2.pookoo.sign.fullname", fullname)

        # Guarantors (page 2, up to 3)
        guarantors = s3.get("guarantors", [])
        for i, g in enumerate(guarantors[:3]):
            n = i + 1
            name = g.get("name", "")
            code = g.get("member_code", "")
            pos = g.get("position", "")
            dept = g.get("department", "")

            if n <= 2:
                sv(f"txt_p2.kumpragun.per{n}.fullname", name)
                sv(f"txt_p2.kumpragun.per{n}.codeno", code)
                sv(f"txt_p2.kumpragun.per{n}.position", pos)
                sv(f"txt_p2.kumpragun.per{n}.dept_name", dept)
            else:
                # Third guarantor: fullname field is under 'per', others under 'per3'
                sv("txt_p2.kumpragun.per.fullname", name)
                sv("txt_p2.kumpragun.per3.codeno", code)
                sv("txt_p2.kumpragun.per3.position", pos)
                sv("txt_p2.kumpragun.per3.dept_name", dept)

        # ── PAGE 3 — Supervisor opinion ───────────────────────────────────────
        sup_sig = s4.get("superior_sig", {})
        opinion = s4.get("superior_opinion")
        sv("chk_p3.supervisor_comments.ch1.t", "Y" if opinion == "true" else "")
        sv("chk_p3.supervisor_comments.ch1.f", "Y" if opinion == "false" else "")
        # ch2/ch3 require additional opinions not currently in the form — leave blank
        sv("chk_p3.supervisor_comments.ch2.t", "")
        sv("chk_p3.supervisor_comments.ch2.f", "")
        sv("chk_p3.supervisor_comments.ch3.t", "")
        sv("chk_p3.supervisor_comments.ch3.f", "")

        if sup_sig.get("signed"):
            sv("sign_p3.supervisor_comments.sign", sup_sig.get("signature_base64"))
            sv("txt_p3.supervisor_comments.fullname", sup_sig.get("signer_name", ""))
            sv("txt_p3.supervisor_comments.position", sup_sig.get("signer_position", ""))

        # ── PAGE 4 — Loan agreement (borrower section) ────────────────────────
        sv("txt_p4.ordinary_loan_agreement.date", thai_date_now)

        sv("txt_p4.ordinary_loan_agreement.pookoo.fullname", fullname)
        sv("txt_p4.ordinary_loan_agreement.pookoo.mem_code", s1.get("member_code", ""))
        sv("txt_p4.ordinary_loan_agreement.pookoo.position", s1.get("position", ""))
        sv("txt_p4.ordinary_loan_agreement.pookoo.dept", s1.get("department", ""))
        sv("txt_p4.ordinary_loan_agreement.pookoo.card_no", s1.get("id_card", ""))

        # Register address (page 4 agreement)
        sv("txt_p4.ordinary_loan_agreement.pookoo.addr.no", addr_register.get("house_no", ""))
        sv("txt_p4.ordinary_loan_agreement.pookoo.addr.moo", addr_register.get("moo", ""))
        sv("txt_p4.ordinary_loan_agreement.pookoo.addr.road", addr_register.get("road", ""))
        sv("txt_p4.ordinary_loan_agreement.pookoo.addr.tambon", addr_register.get("tambon", ""))
        sv("txt_p4.ordinary_loan_agreement.pookoo.amphur", addr_register.get("amphur", ""))
        sv("txt_p4.ordinary_loan_agreement.pookoo.province", addr_register.get("province", ""))

        # Loan amount (ch1 section)
        sv("txt_p4.ordinary_loan_agreement.pookoo.ch1.amount", self._format_num(loan_amount))
        sv("txt_p4.ordinary_loan_agreement.pookoo.ch1.amount_text", amount_text)

        # Contract info (ch2 section)
        sv("txt_p4.ordinary_loan_agreement.pookoo.ch2.ch_no", s6.get("contract_no", ""))
        sv("txt_p4.ordinary_loan_agreement.pookoo.ch2.interest_rate", str(annual_rate))

        # ID type checkbox — default citizen card
        sv("chk_p4.ordinary_loan_agreement.pookoo.citizen_card", "Y")

        # Payment schedule — fill both pay_by_bank and pay_by_coop with same values
        for section in ("pay_by_bank", "pay_by_coop"):
            sv(f"txt_p4.ordinary_loan_agreement.{section}.amount_per_period", self._format_num(monthly_payment))
            sv(f"txt_p4.ordinary_loan_agreement.{section}.amount_per_period_text", monthly_text)
            sv(f"txt_p4.ordinary_loan_agreement.{section}.period_num", str(int(repayment_period)) if repayment_period else "")
            sv(f"txt_p4.ordinary_loan_agreement.{section}.period_text", period_text_words)

        sv("txt_p4.ordinary_loan_agreement.start_month", start_month)

        # Pay method checkbox
        sv("chk_p4.ordinary_loan_agreement.pay_method.by_bank", "Y" if is_transfer else "")
        sv("chk_p4.ordinary_loan_agreement.pay_method.by_coop", "Y" if not is_transfer else "")

        # Borrower signatures (page 4)
        if bsig.get("signed"):
            sv("sign_p4.ordinary_loan_agreement.pookoo.sign", bsig.get("signature_base64"))
            sv("sign_p4.ordinary_loan_agreement.pookoo.sign2", bsig.get("signature_base64"))

        # ── PAGE 5 — Signing page ─────────────────────────────────────────────
        sv("txt_p5.ordinary_loan_agreement.pookoo.fullname", fullname)

        # Witness, Chairman, Manager names
        sv("txt_p5.ordinary_loan_agreement.witness.fullname", s6.get("witness_1_name", ""))
        sv("txt_p5.ordinary_loan_agreement.chairman.fullname", s6.get("chairman_name", ""))
        sv("txt_p5.ordinary_loan_agreement.coop_mgr.fullname", s6.get("manager_name", ""))

        # Received amount info
        sv("txt_p5.ordinary_loan_agreement.recv_info.fullname", fullname)
        sv("txt_p5.ordinary_loan_agreement.recv_info.amount", self._format_num(loan_amount))
        sv("txt_p5.ordinary_loan_agreement.recv_info.amount_text", amount_text)
        sv("txt_p5.ordinary_loan_agreement.recv_info.recv_date", effective_date_thai)

        # Borrower signature (page 5)
        if bsig.get("signed"):
            sv("sign_p5.ordinary_loan_agreement.pookoo.sign3", bsig.get("signature_base64"))
            sv("sign_p5.ordinary_loan_agreement.recv_sign", bsig.get("signature_base64"))

        # Witness signature
        wsig1 = s6.get("witness_sig_1", {})
        if wsig1.get("signed"):
            sv("sign_p5.ordinary_loan_agreement.witness.sign", wsig1.get("signature_base64"))

        # Chairman signature
        chairman_sig = s6.get("chairman_sig", {})
        if chairman_sig.get("signed"):
            sv("sign_p5.ordinary_loan_agreement.chairman.sign", chairman_sig.get("signature_base64"))

        # Manager signature
        mgr_sig = s6.get("manager_sig", {})
        if mgr_sig.get("signed"):
            sv("sign_p5.ordinary_loan_agreement.coop_mgr.sign", mgr_sig.get("signature_base64"))
            sv("sign_p5.ordinary_loan_agreement.pay_sign", mgr_sig.get("signature_base64"))

        # Spouse agreement (page 5)
        spouse_sig = s4.get("spouse_sig", {})
        is_married = s1.get("marital_status") == "married"
        if is_married:
            spouse_name = s1.get("spouse_name", "")
            sv("txt_p5.spouse_agreement.place", addr_register.get("province", ""))
            sv("txt_p5.spouse_agreement.date", thai_date_now)
            sv("txt_p5.spouse_agreement.spouse.fullname", spouse_name)
            sv("txt_p5.spouse_agreement.spouse_of", fullname)
            sv("txt_p5.spouse_agreement.spouse_of2", fullname)
            sv("chk_p5.spouse_agreement.spouse_type.wife", "Y")
            sv("chk_p5.spouse_agreement.spouse_type.husban", "")
            if spouse_sig.get("signed"):
                sv("sign_p5.spouse_agreement.spouse_sign", spouse_sig.get("signature_base64"))
                sv("sign_p5.spouse_agreement.pookoo_sign", bsig.get("signature_base64") if bsig.get("signed") else "")
        else:
            # Single borrower — fill spouse page with dashes
            sv("txt_p5.spouse_agreement.place", "-")
            sv("txt_p5.spouse_agreement.date", "-")
            sv("txt_p5.spouse_agreement.spouse.fullname", "-")
            sv("txt_p5.spouse_agreement.spouse_of", "-")
            sv("txt_p5.spouse_agreement.spouse_of2", "-")

        return pdf_fields

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _format_num(self, val: Any) -> str:
        if val is None:
            return ""
        try:
            return "{:,.0f}".format(float(val))
        except Exception:
            return str(val)

    def _to_thai_date(self, dt: datetime.datetime) -> str:
        thai_months = [
            "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
            "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
        ]
        return f"{dt.day} {thai_months[dt.month - 1]} {dt.year + 543}"

    def _to_thai_month_year(self, dt: datetime.datetime) -> str:
        thai_months = [
            "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
            "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
        ]
        return f"{thai_months[dt.month - 1]} {dt.year + 543}"

    def _parse_date(self, date_str: str) -> datetime.datetime:
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return datetime.datetime.now()

    def _add_one_month(self, dt: datetime.datetime) -> datetime.datetime:
        month = dt.month % 12 + 1
        year = dt.year + (1 if dt.month == 12 else 0)
        day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                            31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return dt.replace(year=year, month=month, day=day)

    def _calc_monthly_payment(self, principal: float, annual_rate_pct: float, months: int) -> float:
        if not principal or not months:
            return 0.0
        r = annual_rate_pct / 100 / 12
        if r == 0:
            return round(principal / months, 2)
        factor = (1 + r) ** months
        return round(principal * r * factor / (factor - 1), 2)

    def _num_to_words(self, n: int) -> str:
        from app.utils.thai_baht import _integer_to_text
        return _integer_to_text(n)

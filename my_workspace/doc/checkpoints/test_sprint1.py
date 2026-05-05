import io
import re
import sys
import warnings
import logging
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings("ignore", message=".*contains characters not supported.*")
logging.getLogger("pypdf").setLevel(logging.ERROR)

import pikepdf
from pikepdf import Pdf, Dictionary, Name, String, Array
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas

# ─────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
INPUT_FILE  = SCRIPT_DIR / "สัญญาเงินกู้สามัญ สอ.ภ.6-fillable.pdf"
OUTPUT_FILE = SCRIPT_DIR / "สัญญาเงินกู้_กรอกสำเร็จ.pdf"
FONT_FILE   = Path(r"F:\programming\python\MTPPR6CoopForm2\my_workspace\backend\app\assets\font\THSarabunNew\THSarabunNew.ttf")
CHECK_IMAGE = Path(r"F:\programming\python\MTPPR6CoopForm2\my_workspace\backend\app\assets\icons\check.png")

FORM_DATA = {
    # --- page 1 ---
    "chk_p1.doc_for_ordinary_loan.ch1.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch1.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch2.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch2.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch3.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch3.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch4.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch4.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch5.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch5.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch6.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch6.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch7.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch7.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch8.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch8.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch9.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch9.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch10.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch10.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch11.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch11.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch12.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch12.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch13.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch13.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch14.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch14.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch15.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch15.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch16.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch16.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch17.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch17.not_have": "",    
    "chk_p1.doc_for_ordinary_loan.ch18.have": "Y",
    "chk_p1.doc_for_ordinary_loan.ch18.not_have": "",    
    "txt_p2.coop_agent.fullname": "มาลี มุ่งทำดี",

    # --- page 2 ---
    "txt_p2.geninfo.write_at":              "สภ.เมืองพิษณุโลก",
    "txt_p2.geninfo.write_date":            "6 เมษายน 2568",
    "txt_p2.pookoo.geninfo.fullname":       "ด.ต. สมชาย รักชาติ",
    "txt_p2.pookoo.geninfo.position":       "ผบ.หมู่ (ป.)",
    "txt_p2.pookoo.geninfo.sangud":         "ภ.จว.พิษณุโลก",
    "txt_p2.pookoo.geninfo.mem_id":         "123456",
    "txt_p2.pookoo.geninfo.card_id":        "1-5501-12345-67-8",
    "chk_p2.pookoo.geninfo.has_sarary":     "Y",
    "chk_p2.pookoo.geninfo.has_wage":       "",
    "txt_p2.pookoo.geninfo_sarary_amount":  "40,000",
    "txt_p2.pookoo.addr.house_no":          "99/1",
    "txt_p2.pookoo.addr.moo_no":            "5",
    "txt_p2.pookoo.addr.road":              "มิตรภาพ",
    "txt_p2.pookoo.addr.tambon":            "ในเมือง",
    "txt_p2.pookoo.addr.amphur":            "เมือง",
    "txt_p2.pookoo.addr.province":          "พิษณุโลก",
    "txt_p2.pookoo.addr2.house_no":         "10",
    "txt_p2.pookoo.addr2.moo_no":           "2",
    "txt_p2.pookoo.addr2.road":             "",
    "txt_p2.pookoo.addr2.tambon":           "วัดจันทร์",
    "txt_p2.pookoo.addr2.amphur":           "เมือง",
    "txt_p2.pookoo.addr2.province":         "พิษณุโลก",
    "chk_p2.pookoo.kooinfo.recv.myself":"",
    "chk_p2.pookoo.kooinfo.recv.book_bank":"Y",
    "txt_p2.pookoo.kooinfo.recv.by_bank.bank_name":"กรุงไทย",
    "chk_p2.pookoo.kooinfo.recv.by_bank.bank_branch":"พรหมพิราม",
    "chk_p2.pookoo.kooinfo.recv.by_bank.account_no":"1234567890",
    "chk_p2.pookoo.kooinfo.recv.by_bank.account_name":"สมชาย รักชาติ",
    "txt_p2.pookoo.sign.fullname":"สมชาย รักชาติ",
    "txt_p2.payarn.sign.fullname":"มาลี มุ่งทำดี"
}

FF_READONLY = 1


# ─────────────────────────────────────────────────────────
#  ลงทะเบียน font THSarabunNew กับ reportlab
# ─────────────────────────────────────────────────────────
def _register_font(font_path: Path):
    if not font_path.exists():
        raise FileNotFoundError(f"ไม่พบ font file: {font_path}")
    pdfmetrics.registerFont(TTFont("THSarabunNew", str(font_path)))


# ─────────────────────────────────────────────────────────
#  สร้าง appearance stream สำหรับ text field ด้วย reportlab
# ─────────────────────────────────────────────────────────
Q_LEFT, Q_CENTER, Q_RIGHT = 0, 1, 2


def _make_appearance(dest_pdf: Pdf, value: str, rect, font_size: float = 16,
                     quadding: int = Q_LEFT):
    """
    คืน pikepdf.Stream ที่เป็น Form XObject (appearance stream)
    พร้อม font resources embed ด้วย reportlab + THSarabunNew
    quadding: 0=Left, 1=Center, 2=Right  (PDF /Q value)
    """
    x1, y1, x2, y2 = [float(v) for v in rect]
    w, h = x2 - x1, y2 - y1

    # สร้าง mini PDF ด้วย reportlab
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=(w, h))
    c.setFont("THSarabunNew", font_size)
    y_pos = max(2.0, (h - font_size) / 2)

    if quadding == Q_CENTER:
        c.drawCentredString(w / 2, y_pos, value)   # กึ่งกลาง
    elif quadding == Q_RIGHT:
        c.drawRightString(w - 2, y_pos, value)      # ชิดขวา
    else:
        c.drawString(2, y_pos, value)               # ชิดซ้าย (default)

    c.save()

    # อ่านด้วย pikepdf แล้วดึง content stream + resources
    buf.seek(0)
    mini = Pdf.open(buf)
    page = mini.pages[0]

    contents = page["/Contents"]
    if isinstance(contents, pikepdf.Array):
        contents = contents[0]
    content_bytes = contents.read_bytes()

    mini_res = page.get("/Resources", Dictionary())

    # สร้าง Form XObject ใน dest_pdf
    ap_stream = dest_pdf.make_stream(content_bytes)
    ap_stream["/Subtype"] = Name.Form
    ap_stream["/BBox"]    = Array([0, 0, w, h])

    # copy resources (Font) จาก mini PDF → dest_pdf
    if "/Font" in mini_res:
        font_dict = Dictionary()
        for fn, fref in mini_res["/Font"].items():
            font_obj = fref.resolve() if hasattr(fref, 'resolve') else fref
            font_dict[fn] = dest_pdf.copy_foreign(font_obj)
        ap_stream["/Resources"] = Dictionary({"/Font": font_dict})

    return ap_stream


# ─────────────────────────────────────────────────────────
#  สร้าง appearance stream สำหรับ checkbox/radio ด้วยภาพ check.png
# ─────────────────────────────────────────────────────────
def _make_check_appearance(dest_pdf: Pdf, rect, img_path: Path):
    """
    คืน pikepdf.Stream ที่เป็น Form XObject แสดงภาพ check.png
    ปรับขนาดพอดีกับ rect ของ field
    """
    x1, y1, x2, y2 = [float(v) for v in rect]
    w, h = x2 - x1, y2 - y1

    buf = io.BytesIO()
    c = Canvas(buf, pagesize=(w, h))
    c.drawImage(str(img_path), 0, 0, width=w, height=h, mask="auto")
    c.save()

    buf.seek(0)
    mini = Pdf.open(buf)
    page = mini.pages[0]

    contents = page["/Contents"]
    if isinstance(contents, pikepdf.Array):
        contents = contents[0]
    content_bytes = contents.read_bytes()

    mini_res = page.get("/Resources", Dictionary())

    ap_stream = dest_pdf.make_stream(content_bytes)
    ap_stream["/Subtype"] = Name.Form
    ap_stream["/BBox"]    = Array([0, 0, w, h])

    # copy XObject resources (image) จาก mini PDF → dest_pdf
    res_dict = Dictionary()
    if "/XObject" in mini_res:
        xobj_dict = Dictionary()
        for xn, xref in mini_res["/XObject"].items():
            xobj = xref.resolve() if hasattr(xref, 'resolve') else xref
            xobj_dict[xn] = dest_pdf.copy_foreign(xobj)
        res_dict["/XObject"] = xobj_dict
    if "/Font" in mini_res:
        font_dict = Dictionary()
        for fn, fref in mini_res["/Font"].items():
            font_obj = fref.resolve() if hasattr(fref, 'resolve') else fref
            font_dict[fn] = dest_pdf.copy_foreign(font_obj)
        res_dict["/Font"] = font_dict
    if res_dict:
        ap_stream["/Resources"] = res_dict

    return ap_stream


# ─────────────────────────────────────────────────────────
#  ซ่อน widget annotation (Hidden flag bit 2)
# ─────────────────────────────────────────────────────────
def _set_hidden(field):
    """ตั้ง /F annotation flag = Hidden (bit 2) ทั้งที่ field และ kids"""
    HIDDEN = 2  # annotation flag bit 2

    def _hide(obj):
        current = int(obj.get("/F", 4))  # default 4 = Print
        obj["/F"] = pikepdf.Object.parse(str(current | HIDDEN).encode())
        # ล้าง appearance stream เพื่อให้ไม่มีอะไรแสดง
        if "/AP" in obj:
            del obj["/AP"]

    _hide(field)
    if "/Kids" in field:
        for k_ref in field["/Kids"]:
            k = k_ref.resolve() if hasattr(k_ref, 'resolve') else k_ref
            _hide(k)


# ─────────────────────────────────────────────────────────
#  navigate AcroForm hierarchy
# ─────────────────────────────────────────────────────────
def _collect_fields(fields_array, parent_path: str, result: dict):
    for field_ref in fields_array:
        field = field_ref if isinstance(field_ref, Dictionary) else field_ref.resolve()
        t = field.get("/T")
        if t is None:
            continue
        name = str(t)
        full = f"{parent_path}.{name}" if parent_path else name
        if "/FT" in field:
            result[full] = field
        if "/Kids" in field:
            _collect_fields(field["/Kids"], full, result)


def build_field_map(pdf: Pdf) -> dict:
    acroform = pdf.Root.get("/AcroForm")
    if not acroform or "/Fields" not in acroform:
        return {}
    result = {}
    _collect_fields(acroform["/Fields"], "", result)
    return result


# ─────────────────────────────────────────────────────────
#  show_fields_summary
# ─────────────────────────────────────────────────────────
def show_fields_summary(input_path: Path) -> None:
    pdf = Pdf.open(str(input_path))
    field_map = build_field_map(pdf)
    if not field_map:
        print("ไม่พบ AcroForm field ใดๆ")
        return
    print(f"\n📋 พบ {len(field_map)} fields ในไฟล์ '{input_path.name}':")
    print(f"   {'Field ID':<55}  {'Type':<6}  Value")
    print("   " + "-" * 80)
    for full_path, field in field_map.items():
        ft  = str(field.get("/FT", "?")).lstrip("/")
        val = field.get("/V", "")
        da  = str(field.get("/DA", "")).strip()
        print(f"   '{full_path:<53}'  {ft:<6}  /DA={da!r}")
    print()


# ─────────────────────────────────────────────────────────
#  fill_pdf — กรอกข้อมูล + embed appearance + lock
# ─────────────────────────────────────────────────────────
def fill_pdf(input_path: Path, output_path: Path, data: dict) -> bool:
    if not input_path.exists():
        print(f"❌ ไม่พบไฟล์: {input_path}")
        return False

    _register_font(FONT_FILE)

    pdf = Pdf.open(str(input_path))
    field_map = build_field_map(pdf)
    if not field_map:
        print("❌ PDF ไม่มี AcroForm field")
        return False

    # ─── match check ────────────────────────────────────
    matched   = [k for k in data if k in field_map]
    unmatched = [k for k in data if k not in field_map]
    if unmatched:
        print(f"⚠️  {len(unmatched)} key ไม่พบใน PDF:")
        for k in sorted(unmatched):
            print(f"     ✗ '{k}'")
    print(f"✔  {len(matched)}/{len(data)} fields matched")

    # ─── กรอกข้อมูล + สร้าง appearance stream ──────────
    print("\n   สร้าง appearance stream ด้วย THSarabunNew...")
    filled = 0
    errors = 0
    for full_path, value in data.items():
        if full_path not in field_map:
            continue
        field = field_map[full_path]

        # ตั้งค่า /V ที่ parent field
        field["/V"] = String(value)

        # chk/rdo ที่ว่าง → ซ่อน widget (Hidden annotation flag)
        is_check = full_path.split(".")[0].startswith(("chk", "rdo"))
        if is_check and not value:
            _set_hidden(field)
            filled += 1
            continue

        if not value:
            filled += 1
            continue

        # หา /Rect → อาจอยู่ที่ parent หรือใน Kid widget
        rect = field.get("/Rect")
        widget = field  # ออบเจกต์ที่จะใส่ /AP

        if rect is None and "/Kids" in field:
            kids = field["/Kids"]
            best_kid = None
            best_area = 0.0
            for k_ref in kids:
                k = k_ref.resolve() if hasattr(k_ref, 'resolve') else k_ref
                r = k.get("/Rect")
                if r is None:
                    continue
                x1, y1, x2, y2 = [float(v) for v in r]
                area = (x2 - x1) * (y2 - y1)
                if area > best_area:
                    best_area = area
                    best_kid = k
                    rect = r
            if best_kid is not None:
                widget = best_kid

        if rect is None:
            print(f"     ⚠️  {full_path}: ไม่พบ /Rect")
            errors += 1
            continue

        # แยก logic: chk/rdo + "Y" → ภาพ check, อื่น ๆ → ข้อความ

        try:
            if is_check and value.upper() == "Y":
                ap_stream = _make_check_appearance(pdf, rect, CHECK_IMAGE)
            else:
                da = str(field.get("/DA", "/THSarabunNew 16 Tf 0 g"))
                m = re.search(r'/THSarabunNew\s+(\d+)', da)
                font_size = float(m.group(1)) if m else 16.0
                quadding  = int(field.get("/Q", 0))  # 0=Left, 1=Center, 2=Right
                ap_stream = _make_appearance(pdf, value, rect, font_size, quadding)

            widget["/AP"] = Dictionary({"/N": ap_stream})
            filled += 1
        except Exception as e:
            print(f"     ⚠️  {full_path}: {e}")
            errors += 1

    print(f"   📝 กรอก {filled} fields  (error={errors})")

    # ─── ตั้ง NeedAppearances = false (มี /AP แล้ว) ─────
    acroform = pdf.Root.get("/AcroForm")
    if acroform:
        if "/NeedAppearances" in acroform:
            del acroform["/NeedAppearances"]

    # ─── ReadOnly flag ทุก field ─────────────────────────
    print("\n   🔒 ตั้ง ReadOnly...")
    for field in field_map.values():
        ff = int(field.get("/Ff", 0))
        field["/Ff"] = pikepdf.Object.parse(str(ff | FF_READONLY).encode())
    print(f"   ✓ Lock {len(field_map)} fields")

    # ─── บันทึก ──────────────────────────────────────────
    try:
        pdf.save(str(output_path))
    except Exception as exc:
        print(f"❌ บันทึกไม่ได้: {exc}")
        return False

    size_kb = output_path.stat().st_size / 1024
    print(f"\n✅ บันทึกแล้ว: {output_path}  ({size_kb:.1f} KB)")
    return True


# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  CoopForm PDF Filler — Test Script")
    print("=" * 60)

    try:
        show_fields_summary(INPUT_FILE)
        success = fill_pdf(INPUT_FILE, OUTPUT_FILE, FORM_DATA)
        sys.exit(0 if success else 1)
    except Exception as exc:
        print(f"\n❌ Unexpected error: {type(exc).__name__}: {exc}")
        import traceback; traceback.print_exc()
        sys.exit(1)

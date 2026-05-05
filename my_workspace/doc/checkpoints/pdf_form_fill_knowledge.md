# องค์ความรู้และ Lesson Learned: Python สำหรับกรอกข้อมูล PDF Form

> **Project:** MTPPR6CoopForm2  
> **ไฟล์ PDF ต้นแบบ:** สัญญาเงินกู้สามัญ สอ.ภ.6-fillable.pdf (สร้างด้วย Adobe Acrobat)  
> **วันที่:** เมษายน 2568

---

## 1. โครงสร้างของ PDF AcroForm

### 1.1 Hierarchy ของ Field

Adobe Acrobat สร้าง field แบบ **tree hierarchy** ไม่ใช่ flat list

```
AcroForm
└── /Fields (root array)
    └── txt_p2  (group node — มี /T แต่ไม่มี /FT)
        └── pookoo  (group node)
            └── geninfo  (group node)
                └── fullname  ← leaf field (มี /FT = /Tx)
```

**Lesson Learned:**  
`pypdf.get_fields()` คืน flat dict โดยรวม path ให้แล้ว เช่น `"txt_p2.pookoo.geninfo.fullname"`  
แต่ widget annotation จริงมี `/T = "fullname"` เท่านั้น  
→ ห้ามใช้ full path เป็น key ตรงๆ กับ `update_page_form_field_values` เพราะจะไม่ match!

### 1.2 ประเภท Field (/FT)

| /FT  | ความหมาย       | วิธีใช้งาน                          |
|------|----------------|--------------------------------------|
| /Tx  | Text field     | กรอกข้อความ                         |
| /Btn | Button/Checkbox| ค่า "Y" = แสดงภาพ, "" = ซ่อน        |
| /Ch  | Choice/Dropdown| กรอก string ตรงกับ option            |
| /Sig | Signature      | ต้องใช้ digital signature library    |

### 1.3 Widget กับ Field แยกกัน

บาง field มีโครงสร้างแบบ:
- **Parent field**: มี `/FT`, `/V`, `/DA`, `/T`, `/Kids` — **ไม่มี /Rect**
- **Child widget**: มี `/Rect`, `/Subtype=/Widget` — **ไม่มี /V**

```python
# ต้องอ่าน /V จาก parent แต่หา /Rect จาก kid
rect = field.get("/Rect")
if rect is None and "/Kids" in field:
    # เลือก kid ที่มีพื้นที่ใหญ่ที่สุด (widget หลัก)
    best_area, best_kid = 0, None
    for k_ref in field["/Kids"]:
        k = k_ref.resolve()
        r = k.get("/Rect")
        if r:
            w = float(r[2]) - float(r[0])
            h = float(r[3]) - float(r[1])
            if w * h > best_area:
                best_area, best_kid, rect = w * h, k, r
    widget = best_kid or field
```

---

## 2. ปัญหาด้าน Font ภาษาไทย

### 2.1 สาเหตุหลัก

Font ใน AcroForm (/DR) แม้จะเป็น `THSarabunNew` แต่ใช้ `/Encoding = /WinAnsiEncoding`  
ซึ่ง **ไม่รองรับ Thai Unicode** (U+0E00–U+0E7F)

```
/DR → /Font → /THSarabunNew:
  /Encoding = /WinAnsiEncoding  ← ปัญหา! รองรับเฉพาะ Latin
  /ToUnicode = (ไม่มี)          ← ทำให้ viewer ต้อง fallback font
```

### 2.2 สิ่งที่ไม่ได้ผล

| วิธี | ผลลัพธ์ |
|------|---------|
| `pypdf.update_page_form_field_values(auto_regenerate=True)` | Warning + ภาษาไทยเป็นกล่องว่าง |
| ตั้ง `NeedAppearances=True` แล้วใช้ `_flatten()` ของ pypdf | Flatten ไม่ render ข้อความ → ข้อมูลหาย |
| `pikepdf.flatten_annotations("all")` | เหมือนกัน — ต้องมี /AP อยู่ก่อน |

### 2.3 วิธีที่ได้ผล: สร้าง Appearance Stream ด้วย reportlab

```python
import io
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
import pikepdf

# 1. ลงทะเบียน font
pdfmetrics.registerFont(TTFont("THSarabunNew", "path/to/THSarabunNew.ttf"))

# 2. สร้าง mini PDF ขนาดเท่ากับ field
def make_appearance(dest_pdf, value, rect, font_size=16, quadding=0):
    x1, y1, x2, y2 = [float(v) for v in rect]
    w, h = x2 - x1, y2 - y1

    buf = io.BytesIO()
    c = Canvas(buf, pagesize=(w, h))
    c.setFont("THSarabunNew", font_size)
    y_pos = max(2.0, (h - font_size) / 2)

    if quadding == 1:   # Center
        c.drawCentredString(w / 2, y_pos, value)
    elif quadding == 2: # Right
        c.drawRightString(w - 2, y_pos, value)
    else:               # Left (default)
        c.drawString(2, y_pos, value)
    c.save()

    # 3. ดึง content stream + font resources จาก mini PDF
    buf.seek(0)
    mini = pikepdf.Pdf.open(buf)
    page = mini.pages[0]
    content_bytes = page["/Contents"].read_bytes()
    mini_res = page.get("/Resources", pikepdf.Dictionary())

    # 4. สร้าง Form XObject ใน dest PDF
    ap = dest_pdf.make_stream(content_bytes)
    ap["/Subtype"] = pikepdf.Name.Form
    ap["/BBox"] = pikepdf.Array([0, 0, w, h])

    if "/Font" in mini_res:
        font_dict = pikepdf.Dictionary()
        for fn, fref in mini_res["/Font"].items():
            font_obj = fref.resolve()
            font_dict[fn] = dest_pdf.copy_foreign(font_obj)
        ap["/Resources"] = pikepdf.Dictionary({"/Font": font_dict})

    return ap

# 5. ใส่ appearance stream เข้า field
field["/AP"] = pikepdf.Dictionary({"/N": ap_stream})
```

---

## 3. Text Alignment (/Q)

PDF spec กำหนด `/Q` (Quadding) สำหรับ text alignment:

| /Q | ความหมาย | reportlab method |
|----|----------|------------------|
| 0  | Left (default) | `drawString(2, y, text)` |
| 1  | Center | `drawCentredString(w/2, y, text)` |
| 2  | Right  | `drawRightString(w-2, y, text)` |

```python
quadding = int(field.get("/Q", 0))
```

---

## 4. Checkbox / Radio Button

### 4.1 โครงสร้าง

- `/FT = /Btn`
- ถ้าค่าเป็น `"Y"` → แสดงภาพ (check icon)
- ถ้าค่าเป็น `""` → ซ่อน widget

### 4.2 การแสดงภาพ check.png

```python
def make_check_appearance(dest_pdf, rect, img_path):
    x1, y1, x2, y2 = [float(v) for v in rect]
    w, h = x2 - x1, y2 - y1

    buf = io.BytesIO()
    c = Canvas(buf, pagesize=(w, h))
    c.drawImage(str(img_path), 0, 0, width=w, height=h, mask="auto")
    c.save()

    buf.seek(0)
    mini = pikepdf.Pdf.open(buf)
    page = mini.pages[0]
    content_bytes = page["/Contents"].read_bytes()
    mini_res = page.get("/Resources", pikepdf.Dictionary())

    ap = dest_pdf.make_stream(content_bytes)
    ap["/Subtype"] = pikepdf.Name.Form
    ap["/BBox"] = pikepdf.Array([0, 0, w, h])

    if "/XObject" in mini_res:
        xobj = pikepdf.Dictionary()
        for xn, xref in mini_res["/XObject"].items():
            xobj[xn] = dest_pdf.copy_foreign(xref.resolve())
        ap["/Resources"] = pikepdf.Dictionary({"/XObject": xobj})

    return ap
```

### 4.3 การซ่อน Widget (Hidden)

```python
# PDF Annotation Flags: bit 2 = Hidden (0x02)
HIDDEN = 2

def set_hidden(field):
    current_f = int(field.get("/F", 4))  # 4 = Print
    field["/F"] = pikepdf.Object.parse(str(current_f | HIDDEN).encode())
    if "/AP" in field:
        del field["/AP"]
    # ซ่อน kids ด้วย
    if "/Kids" in field:
        for k_ref in field["/Kids"]:
            k = k_ref.resolve()
            k["/F"] = pikepdf.Object.parse(str(int(k.get("/F", 4)) | HIDDEN).encode())
```

---

## 5. Navigation AcroForm Hierarchy ด้วย pikepdf

```python
def collect_fields(fields_array, parent_path="", result={}):
    """วน navigate แบบ recursive → {full_path: field_obj}"""
    for field_ref in fields_array:
        field = field_ref.resolve() if hasattr(field_ref, 'resolve') else field_ref
        t = field.get("/T")
        if t is None:
            continue
        full = f"{parent_path}.{t}" if parent_path else str(t)
        if "/FT" in field:        # leaf field
            result[full] = field
        if "/Kids" in field:      # group node
            collect_fields(field["/Kids"], full, result)
    return result

def build_field_map(pdf):
    acroform = pdf.Root.get("/AcroForm")
    if not acroform or "/Fields" not in acroform:
        return {}
    return collect_fields(acroform["/Fields"])
```

---

## 6. Lock Fields (ReadOnly)

```python
FF_READONLY = 1  # Field flag bit 1

for field in field_map.values():
    ff = int(field.get("/Ff", 0))
    field["/Ff"] = pikepdf.Object.parse(str(ff | FF_READONLY).encode())
```

---

## 7. Library ที่ใช้และบทบาท

| Library | เวอร์ชัน | บทบาท |
|---------|---------|-------|
| `pikepdf` | 10.x | อ่าน/เขียน PDF structure, navigate AcroForm, embed resources |
| `pypdf` | 6.x | อ่าน field list (get_fields), ตรวจสอบ metadata |
| `reportlab` | 4.x | สร้าง appearance stream พร้อม font embedding |
| `Pillow` | — | ตรวจสอบขนาด/mode ของ image |

---

## 8. Lesson Learned สรุป

| # | ปัญหา | แนวทางแก้ |
|---|-------|-----------|
| 1 | `pypdf.update_page_form_field_values` ไม่ match field ที่ซ้อนกันลึก | ใช้ `pikepdf` navigate hierarchy เอง + ตั้ง `/V` โดยตรง |
| 2 | Font WinAnsiEncoding ไม่รองรับ Thai | Extract TTF จาก PDF → Register ใน reportlab → สร้าง appearance stream |
| 3 | `_flatten()` ของ pypdf ไม่ render ข้อมูล | ต้องสร้าง `/AP/N` ก่อน flatten หรือใช้ ReadOnly แทน |
| 4 | บาง field ไม่มี `/Rect` ที่ parent | หา `/Rect` จาก child widget (/Kids) โดยเลือกตัวที่มีพื้นที่ใหญ่สุด |
| 5 | ภาษาไทยแสดงผิด font | ใช้ `drawCentredString` / `drawString` ตาม `/Q` ของ field |
| 6 | Checkbox แสดง default UI | สร้าง appearance stream จากรูปภาพ (PNG) แทน |
| 7 | `sys.stdout` บน Windows encode ผิด | ต้องเพิ่ม `sys.stdout.reconfigure(encoding='utf-8')` บรรทัดแรก |

---

## 9. ขั้นตอนการทำงานโดยรวม (Flow)

```
Input PDF (Fillable)
    │
    ├─ pikepdf.Pdf.open()
    ├─ build_field_map()          ← navigate /AcroForm /Fields แบบ recursive
    │
    ├─ For each field in FORM_DATA:
    │    ├─ field["/V"] = value   ← กรอกค่า
    │    ├─ หา /Rect (parent หรือ kid)
    │    ├─ ถ้า chk/rdo + "Y"   → _make_check_appearance() → /AP/N = image
    │    ├─ ถ้า chk/rdo + ""    → _set_hidden()            → /F |= Hidden
    │    └─ ถ้า text             → _make_appearance(quadding) → /AP/N = text
    │
    ├─ Lock ทุก field (/Ff |= ReadOnly)
    └─ pdf.save(output)
```

---

## 10. ไฟล์อ้างอิง

| ไฟล์ | คำอธิบาย |
|------|---------|
| `test.py` | โค้ดหลักสำหรับกรอก PDF |
| `THSarabunNew.ttf` | Font extracted จาก PDF ต้นฉบับ (backup) |
| `../../../backend/app/assets/font/THSarabunNew/` | Font directory ที่ใช้จริง |
| `../../../backend/app/assets/icons/check.png` | ภาพ checkmark สำหรับ checkbox |

# Checkpoint — Sprint 1
**วันที่:** 26 เมษายน 2568  
**Project:** MTPPR6CoopForm2  
**โค้ดหลัก:** `my_workspace/tee_temp/test/test.py`  
**PDF ต้นแบบ:** `my_workspace/tee_temp/test/สัญญาเงินกู้สามัญ สอ.ภ.6-fillable.pdf`

---

## สิ่งที่ทำสำเร็จใน Sprint นี้

### 1. วิเคราะห์ปัญหาและเลือก Library

| Library | บทบาท |
|---------|-------|
| `pikepdf 10.5.1` | navigate AcroForm, ตั้งค่า field, embed resources |
| `reportlab 4.4.10` | สร้าง appearance stream พร้อม font Thai |
| `pypdf 6.8.0` | อ่าน field metadata เบื้องต้น |

### 2. ฟีเจอร์ที่ implement แล้ว

| ฟีเจอร์ | สถานะ | หมายเหตุ |
|---------|-------|---------|
| กรอก text field ภาษาไทย | ✅ | ใช้ reportlab สร้าง appearance stream |
| Font: TH Sarabun New | ✅ | จาก `backend/app/assets/font/THSarabunNew/` |
| Left/Center/Right alignment (`/Q`) | ✅ | อ่านจาก field `/Q` แล้ว pass ไป reportlab |
| Checkbox (chk_) = "Y" → แสดงภาพ | ✅ | ใช้ `check.png` embed ใน appearance stream |
| Checkbox (chk_) = "" → ซ่อน | ✅ | ตั้ง annotation flag `/F \|= Hidden (2)` |
| Lock ทุก field (ReadOnly) | ✅ | `/Ff \|= 1` |
| Navigate field hierarchy (recursive) | ✅ | รองรับ parent+kid หลายระดับ |
| รองรับ field ที่ /Rect อยู่ใน kid | ✅ | เลือก kid ที่มีพื้นที่ใหญ่สุด |
| Flatten PDF | ⚠️ | ยังไม่ทำ — ใช้ ReadOnly แทน |

### 3. สถิติ PDF ต้นแบบ

```
จำนวนหน้า    : 15 หน้า
Field ทั้งหมด : 150 fields
  - /Tx (Text)   : 82 fields
  - /Btn (Check) : 68 fields
Field /Q=Center  : 43 fields
```

### 4. ไฟล์สำคัญ

```
my_workspace/tee_temp/test/
├── test.py                          ← โค้ดหลัก (sprint 1 snapshot)
├── THSarabunNew.ttf                 ← font สำรอง (extracted จาก PDF)
├── doc/
│   └── pdf_form_fill_knowledge.md  ← เอกสารองค์ความรู้
└── สัญญาเงินกู้สามัญ สอ.ภ.6-fillable.pdf

my_workspace/backend/app/assets/
├── font/THSarabunNew/
│   ├── THSarabunNew.ttf
│   ├── THSarabunNew Bold.ttf
│   ├── THSarabunNew Italic.ttf
│   └── THSarabunNew BoldItalic.ttf
└── icons/
    └── check.png  (512x512 RGBA)

my_workspace/tee_temp/doc/checkpoints/
├── checkpoint_sprint1.md   ← ไฟล์นี้
└── test_sprint1.py         ← snapshot ของ test.py
```

---

## โครงสร้างโค้ดหลัก (test.py)

```
Constants
  SCRIPT_DIR, INPUT_FILE, OUTPUT_FILE, FONT_FILE, CHECK_IMAGE

Functions
  _register_font(font_path)
  _make_appearance(dest_pdf, value, rect, font_size, quadding)  ← text field
  _make_check_appearance(dest_pdf, rect, img_path)              ← checkbox
  _set_hidden(field)                                            ← ซ่อน widget
  _collect_fields(fields_array, parent_path, result)            ← recursive nav
  build_field_map(pdf) → dict {full_path: field_obj}
  show_fields_summary(input_path)
  fill_pdf(input_path, output_path, data) → bool

Entry point
  show_fields_summary(INPUT_FILE)
  fill_pdf(INPUT_FILE, OUTPUT_FILE, FORM_DATA)
```

---

## สิ่งที่ยังต้องทำ (Sprint ต่อไป)

- [ ] กรอกข้อมูลครบทุก field (ปัจจุบัน FORM_DATA ครอบคลุมแค่หน้า 2)
- [ ] รองรับ field prefix `sign_` (signature field)
- [ ] รองรับ field prefix `rdo_` (radio button group)
- [ ] Flatten PDF จริง (ต้องการ Ghostscript หรือ pypdfium2)
- [ ] สร้าง API endpoint ใน FastAPI สำหรับรับข้อมูลและสร้าง PDF
- [ ] Unit test สำหรับ field mapping และ appearance

---

## ปัญหาที่พบและวิธีแก้ (Quick Reference)

```
ปัญหา: pypdf.update_page_form_field_values ไม่ match field
แก้:   ใช้ pikepdf navigate /AcroForm /Fields เอง (recursive)

ปัญหา: Thai font แสดงผิด (WinAnsiEncoding)
แก้:   สร้าง appearance stream ด้วย reportlab + TTF file โดยตรง

ปัญหา: บาง field ไม่มี /Rect ที่ parent
แก้:   หา /Rect จาก /Kids widget โดยเลือกตัวที่มีพื้นที่ใหญ่สุด

ปัญหา: _flatten() ของ pypdf ไม่ render ข้อมูล
แก้:   ใช้ /Ff ReadOnly flag แทน (viewer แสดงข้อมูลแต่แก้ไขไม่ได้)

ปัญหา: Windows console ไม่รองรับ UTF-8
แก้:   sys.stdout.reconfigure(encoding='utf-8') บรรทัดแรก
```

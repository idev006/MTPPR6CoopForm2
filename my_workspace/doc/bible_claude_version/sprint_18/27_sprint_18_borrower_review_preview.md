# Sprint 18 — Borrower Review & PDF Preview Step

**วันที่:** 2026-04-29
**เป้าหมาย:** เพิ่มขั้นตอน "ตรวจสอบข้อมูลก่อนส่ง" ให้ผู้กู้ดูสรุปข้อมูลและสร้าง PDF ตัวอย่างได้ ก่อนที่จะยืนยันส่งคำขอให้เจ้าหน้าที่

---

## ที่มาและ Problem Statement

ปัจจุบัน OrdinaryLoanWizard มีปุ่ม "ส่งคำขอรับพิจารณา" อยู่ท้าย Step 4 (ลงนาม) โดยตรง
ผู้กู้ไม่มีโอกาสตรวจสอบว่าข้อมูลที่กรอกทั้งหมดถูกต้องครบถ้วนก่อน submit — โดยเฉพาะ **ข้อมูลบนแบบฟอร์ม PDF** ซึ่งเป็นเอกสารทางกฎหมาย

**Solution:** เพิ่ม Tab ใหม่ "ตรวจสอบข้อมูล" เป็น Tab สุดท้ายของ borrower flow:
1. แสดงสรุปข้อมูลทั้งหมด (ชื่อ, ยอดเงิน, ระยะเวลา, ผู้ค้ำ, ลายเซ็น)
2. ปุ่ม "สร้างตัวอย่าง PDF" → backend สร้าง preview PDF → ผู้กู้กดดูได้
3. กดดู PDF ซ้ำ → ลบไฟล์เก่า + สร้างใหม่อัตโนมัติ
4. เมื่อตรวจสอบแล้ว → กดปุ่ม "ยืนยันและส่งคำขอ" (submit จริง)

---

## Wizard Tab Order (หลัง Sprint 18)

### Borrower View (5 tabs)
```
Tab 1: ข้อมูลผู้กู้        (Step1PersonalInfo)
Tab 2: รายละเอียดเงินกู้   (Step2LoanDetails)
Tab 3: ผู้ค้ำประกัน        (Step3Guarantors)
Tab 4: เอกสารประกอบ        (StepAttachments)
Tab 5: ลงนาม               (Step4SignatureHub)
Tab 6: ตรวจสอบข้อมูล ✨NEW  (StepReview)   ← submit button อยู่ที่นี่
```

### Staff View (8 tabs)
```
Tab 1-6: เหมือน Borrower
Tab 7: ตรวจสอบ (Staff)     (Step5StaffVerification)
Tab 8: สัญญา (Staff)        (Step6ContractFinalization)
```

---

## Milestone Overview

```
M1 — pdf_service.py         เพิ่ม generate_preview_pdf() — บันทึกใน data/previews/
M2 — applications.py        เพิ่ม POST /applications/ordinary/preview endpoint
M3 — applications.py        เพิ่ม GET /applications/preview/download endpoint
M4 — preview.service.ts     Frontend service layer (ไม่ให้ component call API โดยตรง)
M5 — StepReview.vue         Component แสดงสรุป + ปุ่ม PDF preview
M6 — OrdinaryLoanWizard.vue เพิ่ม StepReview tab
M7 — pytest regression       22/22 ผ่าน
M8 — sprint doc + roadmap   อัปเดต
```

---

## M1 — `generate_preview_pdf()` ใน `pdf_service.py`

```python
def generate_preview_pdf(self, form_data: Dict[str, Any], user_id: str) -> Path:
    preview_dir = self.output_dir.parent / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    output_path = preview_dir / f"{user_id}.pdf"

    # ลบ preview เก่าถ้ามี
    if output_path.exists():
        output_path.unlink()

    template_path = self.template_dir / "loan_ordinary_v1.pdf"
    flat_data = self._map_ordinary_loan(form_data)
    success = self.engine.fill_form(template_path, output_path, flat_data)

    if not success:
        raise RuntimeError("Failed to generate preview PDF")
    return output_path
```

---

## M2 — `POST /applications/ordinary/preview`

```
POST /api/v1/applications/ordinary/preview
Auth: Borrower required
Body: OrdinaryLoanSubmit (form_data เต็ม)
Response: { "preview_ready": true, "message": "PDF ตัวอย่างพร้อมแล้ว" }
```

- เรียก `pdf_service.generate_preview_pdf(data, user_id)` ใน threadpool
- ไม่บันทึกข้อมูลลง DB (preview เท่านั้น)
- ถ้า template ไม่มี → 503

---

## M3 — `GET /applications/preview/download`

```
GET /api/v1/applications/preview/download
Auth: Required (borrower)
Response: FileResponse (application/pdf) ชื่อไฟล์ "ตัวอย่าง-แบบขอกู้สามัญ.pdf"
```

- หาไฟล์ `data/previews/{user_id}.pdf`
- ถ้าไม่มี → 404 + message "กรุณาสร้างตัวอย่าง PDF ก่อน"

---

## M4 — `preview.service.ts`

```typescript
export const previewService = {
  async generate(formData: LoanOrdinaryFormData): Promise<void> {
    await apiService.post('/applications/ordinary/preview', formData)
  },
  getDownloadUrl(): string {
    return `${apiService.baseURL}/applications/preview/download`
  }
}
```

---

## M5 — `StepReview.vue`

**Layout:**
```
┌────────────────────────────────────────────────┐
│  📋 สรุปข้อมูลการยื่นขอกู้เงินสามัญ           │
├────────────────────────────────────────────────┤
│  ผู้กู้:    นายสมชาย ใจดี                     │
│  ยอดเงิน:  ฿ 200,000                           │
│  ระยะเวลา: 60 งวด                              │
│  วัตถุประสงค์: ...                             │
│  ผู้ค้ำ:   2 คน                               │
│  ลายเซ็นผู้กู้: ✅ ลงนามแล้ว                  │
├────────────────────────────────────────────────┤
│  [🔍 สร้างตัวอย่าง PDF]  [📄 ดูไฟล์ PDF]     │
│  (spinner ขณะสร้าง)                            │
└────────────────────────────────────────────────┘
```

**States:**
- `idle` — แสดงปุ่ม "สร้างตัวอย่าง PDF"
- `generating` — spinner + ปุ่ม disabled
- `ready` — ปุ่ม "ดูไฟล์ PDF" (เปิด tab ใหม่) + "สร้างใหม่"
- `error` — alert ข้อผิดพลาด

---

## Files จะถูกสร้าง/แก้ไข

| File | Action |
|------|--------|
| `backend/app/services/pdf_service.py` | ✏️ เพิ่ม `generate_preview_pdf()` |
| `backend/app/api/v1/routers/applications.py` | ✏️ เพิ่ม 2 endpoints |
| `frontend/src/services/preview.service.ts` | 🆕 สร้าง |
| `frontend/src/forms/ordinary-loan/StepReview.vue` | 🆕 สร้าง |
| `frontend/src/forms/ordinary-loan/OrdinaryLoanWizard.vue` | ✏️ เพิ่ม StepReview tab |
| `my_workspace/doc/bible_claude_version/11_roadmap.md` | ✏️ อัปเดต Sprint 18 |

---

## Definition of Done

- [x] `generate_preview_pdf()` สร้างไฟล์ใน `data/previews/{user_id}.pdf` (ลบเก่าก่อนสร้างใหม่)
- [x] `POST /applications/ordinary/preview` ทำงานได้ (auth required, ไม่บันทึก DB)
- [x] `GET /applications/preview/download` ส่งไฟล์ PDF ได้ (auth required, FileResponse)
- [x] `preview.service.ts` — service layer (component ไม่ call API โดยตรง)
- [x] `StepReview.vue` — สรุปข้อมูล + 4 states (idle/generating/ready/error)
- [x] ปุ่ม "สร้างตัวอย่าง PDF" → spinner → ปุ่ม "ดูไฟล์ PDF" (เปิด tab ใหม่)
- [x] กดสร้างซ้ำ → ไฟล์เก่าถูกลบ (`output_path.unlink()`) + ไฟล์ใหม่พร้อม
- [x] Tab "ตรวจสอบข้อมูล" อยู่ก่อน submit button (tab สุดท้ายของ borrower)
- [x] Staff ไม่เห็น StepReview (`roles: [ROLES.BORROWER]` เท่านั้น)
- [x] pytest 22/22 passed (ไม่มี regression)

---

## Retrospective

**Lessons Learned:**
- `BaseWizardLayout` ออกแบบ submit button ตาม `isLastTab` — การเพิ่ม StepReview เป็น last tab ของ borrower ทำให้ submit button ย้ายตำแหน่งอัตโนมัติโดยไม่ต้องแก้ BaseWizardLayout
- `StepReview` ไม่ต้องการ `model-value` prop — Vue ส่ง `null` ให้แต่ component ไม่ได้ define prop นั้น จึงไม่มี error (ปกติสำหรับ Vue 3)

**Technics:**
- Preview state machine 4 states (idle/generating/ready/error) ใน local `ref` — ไม่ต้องเพิ่ม state ใน Pinia store เพราะเป็น UI state ของ component นั้นเท่านั้น (ตาม Anti-Pattern: Store Bloat)
- `FileResponse` ของ FastAPI ส่ง `Content-Disposition: attachment` อัตโนมัติ — เพิ่ม filename ให้ browser รู้ชื่อไฟล์

**Cautions:**
- Preview file `data/previews/{user_id}.pdf` ไม่มี expiry — ถ้า user จำนวนมาก disk อาจเต็มได้ในระยะยาว ควรเพิ่ม cleanup job ใน Sprint ถัดไป
- `GET /applications/preview/download` เปิด tab ใหม่ — browser บางตัวอาจ block popup ถ้า user ไม่ได้คลิก button โดยตรง (แต่เราใช้ `window.open` จาก click handler ซึ่งปลอดภัย)

---

## Status: ✅ DONE (2026-04-29)

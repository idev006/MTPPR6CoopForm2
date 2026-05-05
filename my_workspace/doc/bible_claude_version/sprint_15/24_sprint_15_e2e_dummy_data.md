# Sprint 15 — E2E Test: Dummy Data → Web Form → PDF

**วันที่:** 2026-04-29  
**เป้าหมาย:** ทดสอบ end-to-end flow ครบ: กรอกแบบฟอร์มด้วยข้อมูลจำลอง → Submit → ได้ PDF ที่กรอกครบทุก field หน้า 1-5

---

## Milestone Overview

```
M1 — Backend Infrastructure   (Task 1-2)  ← แก้ config + วาง template
M2 — Frontend Dummy Data       (Task 3-4)  ← dummy data + ปุ่มเติมข้อมูล
M3 — User Acceptance Test      (UAT)       ← ผู้ใช้ทดสอบเอง
```

---

## Gap Analysis (พบก่อนเริ่ม Sprint)

| # | ปัญหา | ผลกระทบ |
|---|---|---|
| G1 | `settings.ASSETS_DIR` ไม่มีใน `config.py` | `PdfService()` crash ทันที |
| G2 | `assets/templates/` folder ยังไม่มี | ไม่มี template สำหรับ fill |
| G3 | ไม่มีปุ่ม "เติมข้อมูลทดสอบ" ใน web form | ต้องกรอกมือ 7 steps ใช้เวลานาน ผิดพลาดง่าย |

---

## Task Breakdown

### M1 — Backend Infrastructure

**Task 1: config.py — เพิ่ม ASSETS_DIR**
- เพิ่ม `ASSETS_DIR: str = "app/assets"` ใน Settings class
- ตำแหน่ง: `backend/app/core/config.py`

**Task 2: Copy PDF template**
- สร้าง folder `backend/app/assets/templates/`
- คัดลอก `สัญญาเงินกู้สามัญ สอ.ภ.6-fillable.pdf` → `templates/loan_ordinary_v1.pdf`
- ตำแหน่งต้นฉบับ: `tee_temp/test/สัญญาเงินกู้สามัญ สอ.ภ.6-fillable.pdf`

### M2 — Frontend Dummy Data

**Task 3: สร้าง `src/dev/dummyData.ts`**

ข้อมูลจำลองที่ครอบคลุมทุก field ที่ Zod validation ต้องการ:

```
ผู้กู้:
  - ด.ต.สมชาย ใจดี
  - เลขบัตร: 3101234567891
  - ตำแหน่ง: ผู้บังคับหมู่
  - สังกัด: กก.สส.ภ.จว.เชียงใหม่
  - เงินเดือน: 25,000 บาท
  - ทุนเรือนหุ้น: 150,000 บาท
  - สถานะ: แต่งงาน (เพื่อทดสอบ spouse page)
  - คู่สมรส: นางสาวสมหญิง ใจดี

กู้เงิน:
  - จำนวน: 500,000 บาท
  - งวด: 60 งวด
  - วัตถุประสงค์: ซื้อที่ดินเพื่อปลูกบ้านพักอาศัย
  - วิธีรับ: โอนบัญชี SCB 1234567890

ผู้ค้ำประกัน 2 คน:
  - คนที่ 1: ด.ต.วีระ สุขใจ (โสด) — ทดสอบ single guarantor
  - คนที่ 2: ด.ต.มานะ ตั้งใจ (แต่งงาน) — ทดสอบ guarantor spouse page

ลายเซ็น:
  - ใช้ programmatic PNG base64 (300x80, squiggle line, ~1KB)
  - ทุก signer: borrower, spouse, guarantor×2, guarantor_spouse, superior

Step 5 (checklist):
  - items 0-14: true (มีเอกสาร)
  - items 15-17: false (ไม่มี)

Step 6 (contract):
  - เลขสัญญา: 001/2568
  - วันเริ่ม: 2025-06-01
  - manager_name / chairman_name / witness_1_name / witness_2_name: ครบ
```

**Task 4: เพิ่มปุ่ม "เติมข้อมูลทดสอบ" ใน BaseWizardLayout.vue**
- แสดงเฉพาะ `import.meta.env.DEV` เท่านั้น
- กดแล้ว `fillDummyData()` → set form.step1-6 ทั้งหมด
- ปุ่มสีเหลือง/warning เพื่อแยกออกจาก action จริง

---

## Zod Validation Checklist (ต้องผ่านทั้งหมด)

| Field | ข้อกำหนด | Dummy Value |
|---|---|---|
| step1.id_card | length 13 | `3101234567891` |
| step1.member_code | min 1 | `12345` |
| step1.salary | min 1 | `25000` |
| step1.current_addr | house_no+tambon+amphur+province | ครบ |
| step1.register_addr | house_no+tambon+amphur+province | ครบ |
| step2.loan_amount | min 1000 | `500000` |
| step2.repayment_period | min 1 | `60` |
| step2.loan_purpose | min 5 chars | ครบ |
| step2.bank_account_no | required if transfer | `1234567890` |
| step3.guarantors | min 1 | 2 คน |
| step3.guarantors[].id_card | length 13 | ครบ |
| step3.guarantors[].current_addr | ครบ | ครบ |
| step4.borrower_sig.signed | true | ✓ |
| step4.superior_sig.signed | true | ✓ |

---

## PDF Fields ที่คาดหวัง (Acceptance Criteria)

| หน้า | Field ตัวอย่าง | ค่าที่คาดหวัง |
|---|---|---|
| P2 | fullname | ด.ต.สมชาย ใจดี |
| P2 | amount_text1 | ห้าแสนบาทถ้วน |
| P2 | toonreunhoon_amount | 150,000 |
| P3 | supervisor fullname | ตามที่กรอก |
| P4 | interest_rate | 5.75 |
| P4 | amount_per_period | ~9,608 |
| P4 | start_month | กรกฎาคม 2568 |
| P5 | witness.fullname | ตามที่กรอกใน Step 6 |
| P5 | spouse_agreement.place | จังหวัดตาม register_addr |

---

## Changes Made

| File | การเปลี่ยนแปลง |
|---|---|
| `backend/app/core/config.py` | เพิ่ม `ASSETS_DIR: str = "app/assets"` |
| `backend/app/assets/templates/loan_ordinary_v1.pdf` | คัดลอกจาก tee_temp (1.2MB) |
| `frontend/src/dev/dummyData.ts` | ข้อมูลจำลองครบทุก step + 6 signatures base64 |
| `frontend/src/forms/shared/BaseWizardLayout.vue` | ปุ่ม "🧪 เติมข้อมูลทดสอบ" (DEV only) + dynamic import |

## Definition of Done

- [x] `ASSETS_DIR` ถูกเพิ่มใน config.py
- [x] PDF template อยู่ที่ `assets/templates/loan_ordinary_v1.pdf`
- [x] `dummyData.ts` ครอบคลุมทุก field ที่ Zod ต้องการ
- [x] ปุ่ม "เติมข้อมูลทดสอบ" ปรากฏใน dev mode เท่านั้น
- [x] **[UAT]** กดปุ่ม → form เต็มทุก step ✅
- [x] **[UAT]** กด Submit → API ส่งคืน application_no ✅
- [x] **[UAT]** ดาวน์โหลด PDF → ข้อมูลถูกต้องหน้า 1-5 ✅ (116/193 fields filled, 77 hidden)

## Bug Fixes During UAT

| Bug | ไฟล์ | สาเหตุ | วิธีแก้ |
|---|---|---|---|
| `AttributeError: resolve` | `pdf_engine.py` | pikepdf 9.x returns direct Dict (ไม่มี `.resolve()`) ใน array iteration | เพิ่ม `hasattr(ref, "resolve")` guard ทุก call site (7 จุด) |
| `ResponseValidationError: application_id` | `applications.py:32` | `app.id` เป็น UUID object, schema ต้องการ `str` | เปลี่ยนเป็น `str(app.id)` |

## Status: ✅ DONE (2026-04-29)

# Sprint 14 — กู้สามัญ PDF Complete (Pages 1-5)

**วันที่:** 2026-04-29  
**เป้าหมาย:** ทำให้ PDF กู้สามัญ pages 1-5 ออกมาสมบูรณ์ครบทุก field

---

## Key Finding จาก Gap Analysis

- PDF template มี **193 fields** แต่กระจายอยู่แค่ **pages 1-5** เท่านั้น
- Pages 6-15 เป็น legal contract text — ไม่มี AcroForm fields → พิมพ์ + เซ็นมือตามปกติของสหกรณ์
- pdf_service.py ปัจจุบัน map ได้ **ไม่ถึง 50%** ของ fields ทั้งหมด

## Gaps ที่ต้องแก้

| Gap | Page | สาเหตุ |
|---|---|---|
| register_addr ขาด moo/road/tambon/amphur/province | 2, 4 | ไม่ได้ map |
| Thai number-to-words (amount_text) | 2, 4, 5 | ไม่มี utility |
| Interest rate, monthly payment | 4 | ไม่มีใน config/mapping |
| shares_amount, loan type checkbox chk1/chk2 | 2 | ไม่มีใน mapping |
| Supervisor name/position | 3 | SignatureData ไม่มี signer_name |
| Witness/Chairman/Manager fullname | 5 | SignatureData ไม่มี signer_name |
| start_month, payout checkbox | 4 | ไม่มีใน mapping |
| Spouse agreement place/date | 5 | ไม่ได้ map |
| chk_p3 ch2, ch3 supervisor checkboxes | 3 | ไม่ได้ map |

## Changes

### Frontend
- `types/form.ts` — `SignatureData` + `signer_name?: string`
- `types/form.ts` — `Step6Data` + `manager_name`, `chairman_name`, `witness_1_name`, `witness_2_name`
- `Step4SignatureHub.vue` — input ชื่อ+ตำแหน่งเมื่อผู้บังคับบัญชาลงนาม
- `Step6ContractFinalization.vue` — input ชื่อสำหรับ manager/chairman/witnesses

### Backend
- `app/core/config.py` — `INTEREST_RATE_ORDINARY: float = 5.75`
- `app/utils/thai_baht.py` — `baht_to_text()` utility (new file)
- `app/services/pdf_service.py` — complete `_map_ordinary_loan()` ครบ 193 fields

## Business Rules

- **Interest rate:** ใช้จาก `settings.INTEREST_RATE_ORDINARY` (5.75% สำหรับ version นี้)
- **Monthly payment:** `P * r * (1+r)^n / ((1+r)^n - 1)` โดย r = annual_rate/12
- **Loan type:** default เป็น chk1 (ไม่มีไถ่ถอน) เสมอ
- **start_month:** effective_date + 1 เดือน หรือเดือนถัดไปหากไม่มี effective_date
- **Spouse agreement place:** ใช้ province จาก register_addr ของผู้กู้
- **Pages 6-15:** ไม่มี form fields → ปล่อยว่าง (พิมพ์+เซ็นมือ)

## Definition of Done
- [x] PDF กรอกมาพร้อม amount เป็นตัวหนังสือ ("ห้าแสนบาทถ้วน")
- [x] ที่อยู่ทะเบียนบ้านครบทุก field ทั้งหน้า 2 และ 4
- [x] ชื่อ supervisor ปรากฏบนหน้า 3
- [x] ชื่อ witness/chairman/manager ปรากฏบนหน้า 5
- [x] อัตราดอกเบี้ยและเงินผ่อนต่องวดถูกต้องบนหน้า 4

## Status: ✅ COMPLETE (2026-04-28)

# Sprint 5 — Phase 3 Form Wizard (Step 1–3) + Member Profile

**วันที่:** 2026-04-26  
**สถานะ:** ✅ COMPLETE

---

## Gold / Target

ผู้ใช้ (borrower) สามารถ:
1. แก้ไขข้อมูลส่วนตัวบน ProfilePage ได้
2. กด "ยื่นคำขอกู้" แล้วเข้ามาหน้า ApplicationPage ที่มี form แบบ **tabs**
3. กรอกข้อมูล 3 tab (ข้อมูลส่วนตัว / รายละเอียดเงินกู้ / ผู้ค้ำประกัน) ได้
4. Draft บันทึกอัตโนมัติทุก 30 วินาที และบันทึกมือได้ด้วยปุ่ม "บันทึกร่าง"
5. เปิดหน้าใหม่แล้วยังเห็นข้อมูลเดิม (draft โหลดจาก backend)

---

## Milestones

### M1 — Backend APIs ✅
| Endpoint | Method | สถานะ |
|---|---|---|
| `/members/me/profile` | GET | ✅ |
| `/members/me/profile` | PUT | ✅ |
| `/drafts` | POST | ✅ (upsert by form_type) |
| `/drafts/{form_type}` | GET | ✅ |
| `/drafts/{draft_id}` | PUT | ✅ |

### M2 — Backend Services ✅
- `member_service.py`: get_profile, update_profile (Type A), staff update (Type B)
- `draft_service.py`: get_or_create_draft, get_draft_by_form_type, update_draft + delete_expired_drafts (เดิม)

### M3 — Frontend Services & Types ✅
- `types/member.ts`, `types/draft.ts`
- `services/member.service.ts`, `services/draft.service.ts`
- `composables/useAutoSave.ts` (debounce 30s, saveNow, lastSaved)

### M4 — ProfilePage.vue ✅
- โหลดข้อมูล profile จาก `/members/me/profile`
- แสดงข้อมูลบัญชี (read-only): ชื่อ, อีเมล, รหัสสมาชิก
- แก้ไข Type A fields: ยศ/คำนำหน้า, ตำแหน่ง, สังกัด, หน่วยงาน, โทรศัพท์, ที่อยู่
- บันทึกด้วยปุ่ม + alert success/error

### M5 — FormWizard.vue (Tabs) ✅
- ใช้ DaisyUI v5 `tabs tabs-border` 
- **Tab registry** — เพิ่ม/ลบ tab ได้ที่ `TABS` array เท่านั้น
- Auto-save ด้วย `useAutoSave` (debounce 30s) + ปุ่ม "บันทึกร่าง"
- Navigation: prev/next ปุ่ม + click tab โดยตรง

### M6 — Step Components ✅ (Composition API)
| Component | ไฟล์ | ฟิลด์ |
|---|---|---|
| Step1PersonalInfo | `components/wizard/Step1PersonalInfo.vue` | ยศ, ตำแหน่ง, สังกัด, หน่วยงาน, โทรศัพท์, ที่อยู่ 6 ฟิลด์ |
| Step2LoanDetails | `components/wizard/Step2LoanDetails.vue` | จำนวนเงินกู้, จำนวนงวด, วัตถุประสงค์ + คำนวณงวดเบื้องต้น |
| Step3Guarantors | `components/wizard/Step3Guarantors.vue` | ผู้ค้ำ 2 คน (ชื่อ, ตำแหน่ง, สังกัด, โทรศัพท์) |

---

## สถาปัตยกรรม Form Wizard (Tabs)

```
ApplicationPage.vue
  └── FormWizard.vue  ← จัดการ tabs, draft, auto-save
        ├── TABS registry (เพิ่ม/ลบ tab ที่นี่)
        ├── Step1PersonalInfo.vue  (v-model step1 data)
        ├── Step2LoanDetails.vue   (v-model step2 data)
        └── Step3Guarantors.vue   (v-model step3 data)
```

**Draft form_data structure:**
```json
{
  "step1": { "title": "", "position": "", "department": "", "organization": "",
             "phone": "", "addr_house_no": "", "addr_moo": "", "addr_road": "",
             "addr_tambon": "", "addr_amphur": "", "addr_province": "" },
  "step2": { "loan_amount": null, "loan_purpose": "", "repayment_period": null },
  "step3": {
    "guarantor_1": { "name": "", "position": "", "department": "", "phone": "" },
    "guarantor_2": { "name": "", "position": "", "department": "", "phone": "" }
  }
}
```

---

## Design Decision: Tabs แทน Wizard Steps

**เหตุผล:** ผู้ใช้อยากกระโดดไปแก้ tab ใดก็ได้โดยตรง ไม่ต้อง prev/next ทีละขั้น  
**ข้อดี:** เพิ่ม/ลบ tab ได้ที่ `TABS` array เพียงจุดเดียว ไม่ต้องแก้ template  
**ข้อสังเกต:** `current_step` ใน draft ยังเก็บอยู่ (map เป็น tab index) เพื่อ restore tab ล่าสุดเมื่อโหลดซ้ำ

---

## ไฟล์ที่สร้าง/แก้ไข

### Backend
- `app/schemas/member.py` — MemberProfileRead, MemberProfileUpdate, MemberProfileStaffUpdate
- `app/schemas/draft.py` — DraftCreate, DraftRead, DraftUpdate
- `app/services/member_service.py` — get_profile, update_profile
- `app/services/draft_service.py` — get_or_create_draft, get_draft_by_form_type, update_draft
- `app/api/v1/routers/members.py` — GET/PUT /members/me/profile
- `app/api/v1/routers/drafts.py` — POST/GET/PUT /drafts

### Frontend
- `src/types/member.ts` — MemberProfile, MemberProfileUpdate
- `src/types/draft.ts` — DraftSession, DraftUpdate
- `src/services/member.service.ts` — getProfile, updateProfile
- `src/services/draft.service.ts` — createOrGet, getByFormType, update
- `src/composables/useAutoSave.ts` — debounce + saveNow
- `src/pages/ProfilePage.vue` — ✅ complete
- `src/pages/ApplicationPage.vue` — โหลด draft แล้ว mount FormWizard
- `src/components/wizard/FormWizard.vue` — tabs + auto-save
- `src/components/wizard/Step1PersonalInfo.vue`
- `src/components/wizard/Step2LoanDetails.vue`
- `src/components/wizard/Step3Guarantors.vue`
- `src/pages/DashboardPage.vue` — ปุ่ม "ยื่นคำขอ" เปิดใช้งาน

---

## Sprint ถัดไป: Sprint 6 — Phase 3 Steps 4–5

**เป้าหมาย:** Form ครบ 5 steps (เพิ่ม Step4Signatures + Step5Review)

**งานที่ต้องทำ:**
1. Frontend: `Step4Signatures.vue` — UiSignaturePad.vue wrapper (signature_pad library)
2. Frontend: `Step5Review.vue` — สรุปข้อมูลก่อน submit
3. Frontend: `useSignature.ts` — lifecycle + base64 export
4. Backend: Zod validation schemas สำหรับ loan_ordinary form data
5. UX: pre-fill Step1 จาก profile ที่บันทึกไว้

**วิธีเพิ่ม tab ใน Sprint 6:**
```typescript
// ใน FormWizard.vue — เพิ่มที่ TABS array เท่านั้น
{ key: 'step4', label: 'ลายเซ็น', component: Step4Signatures },
{ key: 'step5', label: 'ตรวจสอบ', component: Step5Review },
```

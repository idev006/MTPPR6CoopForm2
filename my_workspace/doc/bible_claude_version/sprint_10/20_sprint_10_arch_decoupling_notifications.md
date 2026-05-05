# 20 — Sprint 10: Architectural Decoupling & Notifications

**วันที่:** 2026-04-28
**สถานะ:** ✅ COMPLETE (partial scope change — ดู Audit)

---

## 20.1 Overview

Sprint 10 เดิมวางแผนไว้สำหรับ Emergency Loan + Notification System ใหม่ทั้งหมด  
แต่ระหว่าง sprint พบว่าปัญหาด้าน **architectural coupling** มีความเร่งด่วนกว่า  
จึงเปลี่ยน scope เป็น refactor โครงสร้าง + แก้ bug backend + เพิ่ม Toast + แก้ Draft

> ดู [§20.5 Audit](#205-audit-แผนเดิม-vs-สิ่งที่ทำจริง) สำหรับรายละเอียดว่าอะไรเปลี่ยนและทำไม

---

## 20.2 สิ่งที่ทำในสปรินท์นี้

### 1. Architectural Decoupling — Form Modularization

**ปัญหาเดิม:** Wizard components ทั้งหมดอยู่ใน `src/components/wizard/` รวมกัน  
ถ้ามีแบบฟอร์มหลายประเภท (กู้สามัญ, กู้ฉุกเฉิน, ฯลฯ) โค้ดจะ tight-couple กัน

**วิธีแก้:** ย้ายมาที่ `src/forms/` แบบ modular:

```
src/forms/
├── ordinary-loan/     ← กู้สามัญ (active)
├── emergency-loan/    ← กู้ฉุกเฉิน (created, hidden — ยังไม่ active)
├── shared/            ← ใช้ร่วมกัน: PersonalInfo, Attachments, Signatures
└── staff/             ← Staff-only: Step5Review, Step6Contract
```

**ผลลัพธ์:**
- Import ใช้ `@/forms` alias แทน `@/components/wizard`
- Router ใช้ `redirect` เพื่อ backward compatibility
- รองรับ 100+ form types ในอนาคต

---

### 2. Backend Bug Fixes — Notification Router

**Bug 1: `ModuleNotFoundError`**
```python
# ก่อน (ผิด)
from app.core.auth import current_user, db_session

# หลัง (ถูก)
from app.core.dependencies import CurrentUser, DbSession
```

**Bug 2: `AttributeError` — UUID/String mismatch**
- `NotificationService` รับ `user_id` เป็น `str` แต่ SQL ต้องการ `UUID`
- แก้: เพิ่ม auto-conversion `uuid.UUID(user_id)` ใน service

---

### 3. Global Toast System

**ไฟล์ใหม่:** `src/stores/toast.store.ts`
- type: `'success' | 'error' | 'info'`
- auto-dismiss หลัง 4 วินาที
- integrate ใน `AppLayout.vue` (corner popup)

**ตัวอย่างการใช้:**
```typescript
const toast = useToastStore()
toast.show('success', 'บันทึกร่างสำเร็จ')
```

---

### 4. Auto Draft Creation Fix

**ปัญหาเดิม:** หน้า `OrdinaryApplicationPage` ไม่ได้ create draft โดยอัตโนมัติ  
ทำให้ปุ่ม "บันทึกร่าง" error ในบางกรณี

**แก้:** `form.store.ts` เพิ่ม `createOrGet()` action  
`OrdinaryApplicationPage.vue` เรียก `form.createOrGet()` ใน `onMounted`

---

## 20.3 ไฟล์ที่สร้าง / แก้ไข

### ใหม่
- `src/forms/ordinary-loan/` — ย้ายจาก `src/components/wizard/`
- `src/forms/emergency-loan/` — โครงสร้างพร้อม, hidden
- `src/forms/shared/` — PersonalInfo, Attachments, Signatures
- `src/forms/staff/` — Step5, Step6
- `src/stores/toast.store.ts`

### แก้ไข
- `src/stores/form.store.ts` — เพิ่ม `createOrGet()`
- `src/pages/OrdinaryApplicationPage.vue` — เรียก `createOrGet()` ใน `onMounted`
- `AppLayout.vue` — integrate Toast component
- `src/router/index.ts` — เพิ่ม redirect สำหรับ backward compat
- `app/api/v1/routers/notifications.py` — แก้ import path
- `app/services/notification_service.py` — แก้ UUID conversion

---

## 20.4 Sprint Retrospective

### 🎓 Lessons Learned
- **BaseLayout Pattern** ช่วยลด DRY ใน Wizard อย่างมาก
- Notification system ที่มีอยู่แล้วมี bug ระดับ import — ควรทดสอบตั้งแต่ต้น

### 💡 Technics
- **Loose Coupling (Form Modularization):** แยก Page + Route + Wizard ตามประเภทแบบฟอร์ม
- **Real-time Polling (Frontend):** Polling ง่ายๆ บน Navbar แทน WebSocket ในระยะแรก
- **Modular Routes + redirect:** รักษา backward compat ขณะ refactor

### ❌ Mistakes
- พยายามรวม Logic ทั้งหมดไว้ใน file เดียวตอนแรก → tight coupling → ต้อง refactor

### ⚠️ Cautions
- เมื่อมีแบบฟอร์ม 100+ ตัว อาจต้องแยก **Pinia store ตามประเภท** แทน global store

---

## 20.5 Audit: แผนเดิม vs สิ่งที่ทำจริง

| งาน | แผนเดิม | ทำจริง | สถานะ |
|---|---|---|---|
| Emergency Loan Backend (model, migration, service) | ✅ วางแผนไว้ | ไม่ได้ทำ | ⏭️ เลื่อนไป Sprint 11 |
| Emergency Loan PDF Template | ✅ วางแผนไว้ | ไม่ได้ทำ | ⏭️ เลื่อนไป Sprint 11 |
| Emergency Loan Frontend Wizard | ✅ วางแผนไว้ | สร้าง directory แต่ hidden | 🟡 Partial |
| Notification Model + Migration | ✅ วางแผนไว้ | ไม่ได้ทำ (model อาจมีอยู่แล้ว) | ⏭️ ตรวจสอบ |
| Notification API `GET /notifications` | ✅ วางแผนไว้ | router มีแล้ว แต่ buggy → แก้ bug | 🟡 Partial |
| NotificationBell.vue + notification.store.ts | ✅ วางแผนไว้ | ทำแล้ว (มีอยู่ก่อน Sprint 10) | ✅ Done |
| **Form Modularization** (`src/forms/`) | ❌ ไม่ได้วางแผน | ทำแล้ว ✅ | ✅ Done |
| **Toast System** | ❌ ไม่ได้วางแผน | ทำแล้ว ✅ | ✅ Done |
| **Auto Draft Fix** | ❌ ไม่ได้วางแผน | ทำแล้ว ✅ | ✅ Done |
| **Backend Import Bug Fix** | ❌ ไม่ได้วางแผน | ทำแล้ว ✅ | ✅ Done |

### สิ่งที่ยังค้างอยู่ → Sprint 11
1. Emergency Loan: backend model + migration + PDF template + full wizard
2. Notification: ตรวจสอบว่า model/migration มีอยู่แล้วหรือไม่ → complete ถ้าขาด

---

## 20.6 Sprint ถัดไป: Sprint 11 — Emergency Loan (กู้ฉุกเฉิน)

**เป้าหมาย:** Emergency Loan form ใช้งานได้จริง end-to-end

**งานที่ต้องทำ:**
1. Backend: `EmergencyLoanService` + PDF mapping สำหรับ template ใหม่
2. Backend: ตรวจสอบ/สร้าง Notification model + migration ถ้ายังไม่มี
3. Frontend: เปิด `src/forms/emergency-loan/` (ปัจจุบัน hidden)
4. Frontend: `FormWizard.vue` โหลด steps ตาม `formType`
5. E2E test: กู้ฉุกเฉิน submit → PDF ออกมาถูกต้อง

# 21 — Sprint 11: StepAttachments Refactor, Emergency Loan E2E, Pre-fill Fix

**วันที่:** 2026-04-28
**สถานะ:** ✅ COMPLETE

---

## 21.1 Overview

Sprint 11 ปิด 3 งานที่ค้างจาก Sprint 10 + Audit:

1. **[REFACTOR]** StepAttachments — แก้ ADR-008 Architecture Violation (direct API calls in component)
2. **[FEATURE]** Emergency Loan End-to-End — wizard มีอยู่แล้ว แต่ pages ขาด draft logic
3. **[FIX]** Pre-fill Step1 from profileStore — chain หัก 3 จุด

---

## 21.2 [REFACTOR] StepAttachments → attachment.service.ts

### ปัญหา (ADR-008)

`StepAttachments.vue` เรียก `api.get / api.post / api.delete` โดยตรงใน component  
ละเมิด §11 Component Communication Architecture: HTTP calls ต้องอยู่ใน `src/services/` เท่านั้น

```typescript
// ก่อน — ADR-008 violation
import api from '@/services/api.service'
const loadFiles = async () => {
  const res = await api.get<Attachment[]>(`/attachments/applications/${applicationId}`)
  attachments.value = res.data
}
```

นอกจากนี้ยังใช้ `alert()` แทน Toast System

### วิธีแก้

**สร้าง `src/services/attachment.service.ts`** — service ใหม่รับ HTTP calls ทั้งหมด:

```typescript
import api from './api.service'

export interface Attachment {
  id: string
  file_type: string
  original_filename: string
  file_size_bytes: number
}

export const attachmentService = {
  async list(applicationId: string): Promise<Attachment[]> {
    const res = await api.get<Attachment[]>(`/attachments/applications/${applicationId}`)
    return res.data
  },
  async upload(applicationId: string, file: File, fileType: string): Promise<void> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', fileType)
    await api.post(`/attachments/applications/${applicationId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  async remove(id: string): Promise<void> {
    await api.delete(`/attachments/${id}`)
  },
}
```

**แก้ `StepAttachments.vue`:**
- ลบ `import api`
- เพิ่ม `import { attachmentService, type Attachment }`
- เพิ่ม `import { useToastStore }`
- เปลี่ยน `alert()` → `toast.show()`
- typed `attachments` ref เป็น `Attachment[]`

### ผลลัพธ์

- Component ไม่รู้จัก HTTP layer อีกต่อไป
- Error handling ผ่าน Toast (consistent กับทั้งระบบ)
- ADR-008 ปิด

---

## 21.3 [FEATURE] Emergency Loan End-to-End

### ปัญหา

Emergency Loan Wizard (`EmergencyLoanWizard.vue`) และ route `/apply/emergency` มีอยู่แล้ว  
แต่ `EmergencyApplicationPage.vue` ไม่มี draft logic เลย — ตั้ง `formType` แล้วหยุด:

```vue
<!-- ก่อน — ไม่มี draft logic -->
onMounted(async () => {
  form.formType = 'loan_emergency'
})
```

### วิธีแก้

เพิ่ม draft load/create + prefill pattern เหมือน OrdinaryApplicationPage:

```typescript
onMounted(async () => {
  form.formType = 'loan_emergency'
  await profile.fetch()
  const existing = await draftService.getByFormType('loan_emergency')
  if (existing) {
    form.initFromDraft(existing)
  } else {
    await form.startNewDraft()
    form.prefillStep1IfEmpty(profile.step1Prefill)
  }
})
```

### ปัญหาย่อย: StepEmergencyData duplicate

`StepEmergencyDetails.vue` export interface `StepEmergencyData` ซ้ำกับ `@/types/form`  
และ `form.store.ts` import จาก `.vue` file — non-standard dependency chain

**แก้:**
- ลบ interface ออกจาก `StepEmergencyDetails.vue`
- เพิ่ม `import type { StepEmergencyData } from '@/types/form'`
- `form.store.ts` import จาก `@/types/form` (SSOT)

### ผลลัพธ์

- Emergency Loan สามารถ submit ได้ end-to-end
- Draft บันทึก/โหลดได้ปกติ
- Single source of truth สำหรับ `StepEmergencyData`

---

## 21.4 [FIX] Pre-fill Step1 from profileStore

### ปัญหา — 3 จุดหัก

**จุดที่ 1: `profileStore.step1Prefill` — wrong field mapping**

computed พยายาม map `p.addr_house_no` ตรงๆ แต่ `Step1Data` ใช้ nested `current_addr: AddressInfo`  
ผลคือ address ไม่เคย prefill ได้เลย

```typescript
// ก่อน — ผิด
return {
  title: p.title,
  addr_house_no: p.addr_house_no,  // ← key ผิด, Step1Data ไม่มี flat addr_*
  ...
}
```

**จุดที่ 2: `form.store.ts` — ไม่มี `prefillStep1IfEmpty` action**

`OrdinaryApplicationPage` เรียก `form.prefillStep1IfEmpty(...)` แต่ function นี้ไม่มีใน store  
→ silent fail (call undefined function)

**จุดที่ 3: Application Pages — ไม่มี draft load/create**

`OrdinaryApplicationPage.vue` ไม่ check existing draft → browser refresh สร้าง draft ใหม่ทุกครั้ง

### วิธีแก้

**`profile.store.ts`** — rewrite `step1Prefill` computed ให้ถูกต้อง:

```typescript
const step1Prefill = computed<Partial<Step1Data>>(() => {
  if (!profile.value) return {}
  const p = profile.value
  return {
    title: p.title ?? '',
    first_name: p.first_name ?? '',
    last_name: p.last_name ?? '',
    member_code: p.member_code ?? '',
    id_card: p.national_id ?? '',
    position: p.position ?? '',
    department: p.department ?? '',
    organization: p.organization ?? '',
    phone: p.phone ?? '',
    salary: p.salary ?? null,
    shares_amount: p.shares_amount ?? null,
    existing_debt: p.existing_debt ?? null,
    current_addr: {
      house_no: p.addr_house_no ?? '',
      moo: p.addr_moo ?? '',
      road: p.addr_road ?? '',
      tambon: p.addr_tambon ?? '',
      amphur: p.addr_amphur ?? '',
      province: p.addr_province ?? '',
    },
  }
})
```

**`form.store.ts`** — เพิ่ม action + return:

```typescript
function prefillStep1IfEmpty(data: Partial<Step1Data>) {
  if (step1.first_name || step1.last_name || step1.member_code) return
  Object.assign(step1, data)
}
```

**`OrdinaryApplicationPage.vue`** — เพิ่ม draft check:

```typescript
onMounted(async () => {
  form.formType = 'loan_ordinary'
  await profile.fetch()
  const existing = await draftService.getByFormType('loan_ordinary')
  if (existing) {
    form.initFromDraft(existing)
  } else {
    await form.startNewDraft()
    form.prefillStep1IfEmpty(profile.step1Prefill)
  }
})
```

### ผลลัพธ์

Pre-fill chain ทำงานครบ end-to-end:
`profileStore.step1Prefill` → `form.prefillStep1IfEmpty()` → `step1` reactive state → `Step1PersonalInfo.vue`

---

## 21.5 Files Changed

| File | Action | เหตุผล |
|------|--------|--------|
| `src/services/attachment.service.ts` | **CREATE** | ADR-008 — extract HTTP logic |
| `src/forms/shared/StepAttachments.vue` | **MODIFY** | ใช้ attachmentService แทน api direct |
| `src/stores/profile.store.ts` | **MODIFY** | แก้ step1Prefill — nested addr structure |
| `src/stores/form.store.ts` | **MODIFY** | เพิ่ม prefillStep1IfEmpty action |
| `src/pages/OrdinaryApplicationPage.vue` | **MODIFY** | เพิ่ม draft load/create + prefill |
| `src/pages/EmergencyApplicationPage.vue` | **MODIFY** | เพิ่ม draft load/create + prefill |
| `src/forms/emergency-loan/StepEmergencyDetails.vue` | **MODIFY** | ลบ duplicate interface, import จาก @/types/form |
| `doc/bible_claude_version/audits/audit_2026_04_28.md` | **CREATE** | Full audit report — 10 findings |
| `doc/bible_claude_version/12_decisions.md` | **MODIFY** | เพิ่ม ADR-008 |
| `doc/bible_claude_version/11_roadmap.md` | **MODIFY** | Sprint 11 TODO, Phase 4/5 status |
| `doc/bible_claude_version/04_architecture.md` | **MODIFY** | Sync กับ Sprint 10 reality |
| `doc/bible_claude_version/07_frontend.md` | **MODIFY** | Directory structure Sprint 10 layout |
| `doc/bible_claude_version/02_requirements.md` | **MODIFY** | BR-05 max 3 guarantors (Sprint 6) |
| `doc/bible_claude_version/README.md` | **MODIFY** | Sprint 9/10 sprint log |
| `doc/bible_claude_version/05_database.md` | **MODIFY** | Migration plan sync |
| `doc/bible_claude_version/03_actors_usecases.md` | **MODIFY** | UC-03 full 7-tab workflow |

---

## 21.6 Architecture Notes

### Service Layer Contract (§11 reinforced)

หลัง Sprint 11 ไม่มี component ใดเรียก `api.*` โดยตรงอีกแล้ว  
ทุก HTTP call ต้องผ่าน `src/services/*.service.ts` เท่านั้น

### Type SSOT

`src/types/form.ts` เป็น single source of truth สำหรับ form interfaces ทั้งหมด  
ห้าม re-export หรือ define interface เดิมซ้ำใน `.vue` files

### Draft Pattern (ทั้ง 2 form types)

```
onMounted → setFormType → profile.fetch()
  → draftService.getByFormType()
    ├── found  → form.initFromDraft()
    └── not found → form.startNewDraft() → form.prefillStep1IfEmpty()
```

---

## 21.7 Sprint Statistics

- **Files Created:** 3 (attachment.service.ts, sprint doc, audit report)
- **Files Modified:** 13+
- **Bugs Fixed:** 3 (pre-fill chain, duplicate type, missing draft logic)
- **Architecture Violations Resolved:** 1 (ADR-008)
- **Status:** COMPLETED ✅

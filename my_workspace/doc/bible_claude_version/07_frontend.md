# 07 — Frontend Architecture & UI Design

---

## 7.1 Design Philosophy — Loose Coupling

### หลักการที่ตกลงกัน

```
Share (UI Primitives)        Shared Steps (ข้ามหลาย form)   Isolate (per form type)
─────────────────────        ──────────────────────────────   ────────────────────────
UiSignaturePad.vue           forms/shared/Step1PersonalInfo   forms/ordinary-loan/
AddressFields.vue            forms/shared/StepAttachments     forms/emergency-loan/
AppNavbar.vue                forms/shared/Step4SignatureHub
ThemePicker.vue              forms/shared/BaseWizardLayout
                             forms/staff/Step5Verification
                             forms/staff/Step6Contract

Rule: ถ้า component เป็นแค่ HTML+style+event → components/ui/ หรือ components/
      ถ้า step ใช้ได้กับ form หลายประเภท → forms/shared/
      ถ้า step ผูกกับ form type เดียว → forms/{form-type}/
```

### ผลลัพธ์ที่ได้

- แก้ validation rule ของ `ordinary-loan` → ไม่กระทบ `emergency-loan` เลย
- เพิ่มแบบฟอร์มใหม่ = สร้าง folder ใหม่ ไม่แตะ code เก่า
- ลบแบบฟอร์มทิ้ง = ลบ folder เดียว ไม่มี side effect

---

## 7.2 Directory Structure

> **หมายเหตุ Sprint 10:** components ทั้งหมดที่เกี่ยวกับ form ย้ายจาก `src/components/wizard/` มาอยู่ที่ `src/forms/` เพื่อ loose coupling ตาม ADR-003

```
frontend/src/
├── main.ts
├── App.vue
│
├── assets/
│   └── main.css                     ← @import tailwindcss + @plugin daisyui + @theme
│
├── components/
│   ├── ui/                          ← LAYER 1: Shared UI Primitives
│   │   └── UiSignaturePad.vue       ← signature_pad wrapper
│   ├── AppLayout.vue                ← min-h-screen + AppNavbar + <slot>
│   ├── AppNavbar.vue                ← logo + ThemePicker + user dropdown
│   ├── ThemePicker.vue              ← 32 DaisyUI themes + swatches
│   ├── AddressFields.vue            ← 6 ช่องที่อยู่ (reused ใน Profile + Step1)
│   └── NotificationBell.vue         ← polling-based notification bell
│
├── forms/                           ← LAYER 2: Form-specific (Isolated per type — Sprint 10)
│   ├── ordinary-loan/               ← กู้สามัญ (active)
│   │   ├── OrdinaryLoanWizard.vue   ← TABS registry + role filter
│   │   ├── Step2LoanDetails.vue
│   │   └── Step3Guarantors.vue
│   │
│   ├── shared/                      ← Steps ที่ใช้ร่วมกันหลาย form types
│   │   ├── Step1PersonalInfo.vue    ← personal info + 2 addresses + income
│   │   ├── StepAttachments.vue      ← upload PDF ⚠️ ADR-008 (direct API call)
│   │   ├── Step4SignatureHub.vue    ← signature pad ทุกฝ่าย (Tablet Walk)
│   │   └── BaseWizardLayout.vue     ← tabs UI + save/submit controls
│   │
│   ├── staff/                       ← Staff-only steps
│   │   ├── Step5StaffVerification.vue  ← 18-item checklist + limit analysis
│   │   └── Step6ContractFinalization.vue ← contract no. + board signatures
│   │
│   └── emergency-loan/              ← กู้ฉุกเฉิน (hidden — Sprint 11 จะเปิด)
│       └── EmergencyLoanWizard.vue  ← stub
│
├── composables/
│   └── useAuth.ts                   ← auth state helpers
│
├── pages/                           ← Route-level components (บาง — orchestrate เท่านั้น)
│   ├── LoginPage.vue
│   ├── DashboardPage.vue            ← borrower: ประวัติคำขอ + สถานะ
│   ├── ProfilePage.vue
│   ├── OrdinaryApplicationPage.vue  ← mount OrdinaryLoanWizard + createOrGet draft
│   └── staff/
│       ├── StaffDashboardPage.vue   ← stats + รายการคำขอทั้งหมด
│       └── ReviewPage.vue           ← detail + approve/reject
│
├── stores/                          ← Pinia (centralized state)
│   ├── auth.store.ts                ← user, token, role
│   ├── form.store.ts                ← form data ทุก step + auto-save + submit
│   ├── profile.store.ts             ← member profile + step1Prefill computed
│   ├── ui.store.ts                  ← theme (localStorage: coopform-theme)
│   ├── toast.store.ts               ← global toast (Sprint 10)
│   └── notification.store.ts        ← bell notifications
│
├── services/                        ← API calls (ทุก HTTP request ต้องผ่านที่นี่)
│   ├── api.service.ts               ← Axios instance + interceptors + auto-refresh
│   ├── auth.service.ts
│   ├── member.service.ts
│   ├── draft.service.ts
│   └── application.service.ts
│
├── schemas/
│   └── validation.ts                ← Zod: ordinaryLoanSchema + emergencyLoanSchema
│
├── router/
│   └── index.ts                     ← route guards (auth + role) + redirect backward compat
│
├── types/
│   ├── form.ts                      ← SSOT: Step1-6Data, GuarantorInfo, SignatureData, LoanOrdinaryFormData, LoanEmergencyFormData
│   ├── member.ts
│   ├── draft.ts
│   └── user.ts
│
└── constants/
    └── roles.ts                     ← ROLES.BORROWER, ROLES.STAFF
```

---

## 7.3 Form Wizard Flow (Sprint 10 Architecture)

### OrdinaryLoanWizard.vue — TABS Registry

```
OrdinaryLoanWizard.vue คือ "Smart Orchestrator" ของ ordinary loan
รู้จัก: tabs ทั้งหมด, role filter, current step data, update handlers

ALL_TABS = [
  { label: 'ข้อมูลผู้กู้',      component: Step1PersonalInfo,     roles: [borrower, staff] },
  { label: 'รายละเอียดเงินกู้',  component: Step2LoanDetails,      roles: [borrower, staff] },
  { label: 'ผู้ค้ำประกัน',       component: Step3Guarantors,       roles: [borrower, staff] },
  { label: 'เอกสารประกอบ',       component: StepAttachments,       roles: [borrower, staff] },
  { label: 'ลงนาม',             component: Step4SignatureHub,      roles: [borrower, staff] },
  { label: 'ตรวจสอบ (Staff)',    component: Step5StaffVerification, roles: [staff] },
  { label: 'สัญญา (Staff)',      component: Step6ContractFinalization, roles: [staff] },
]

tabs = computed(() => ALL_TABS.filter(t => auth.hasRole(t.roles)))
```

### BaseWizardLayout.vue — Dumb Layout

```
BaseWizardLayout รับ props:
  - tabs, current-tab, saving, save-error, last-saved-text
  - is-dirty, submitting, submit-error, can-submit

BaseWizardLayout ไม่รู้จัก:
  - ข้อมูลใน form
  - business logic ใดๆ

Emits: set-tab, save, submit, prev, next
```

### OrdinaryApplicationPage.vue — Route Container

```vue
<!-- OrdinaryApplicationPage.vue -->
<script setup>
const form = useFormStore()
onMounted(async () => {
  await form.createOrGet()  // สร้างหรือโหลด draft อัตโนมัติ
})
</script>
<template>
  <AppLayout>
    <OrdinaryLoanWizard />
  </AppLayout>
</template>
```

---

## 7.4 Step Component Contract

ทุก Step component ต้องปฏิบัติตาม interface นี้:

```typescript
// types/form.types.ts
interface StepComponent {
  // Exposed ให้ FormWizard ใช้
  validate: () => Promise<boolean>   // validate แล้วคืน pass/fail
  getData: () => Record<string, any> // คืน form data ของ step นี้
  prefill: (data: any) => void       // รับ pre-fill data จาก profile
}
```

```vue
<!-- ตัวอย่าง Step1PersonalInfo.vue -->
<script setup lang="ts">
const { validate, getData } = useFormStep()  // composable ที่ทุก step ใช้ร่วม

// Expose ให้ parent (FormWizard) ใช้
defineExpose({ validate, getData })
</script>
```

---

## 7.5 Signature Pad Component

```vue
<!-- UiSignaturePad.vue -->
<!--
  Props: width, height, label, required
  Emits: change(base64: string), clear
  Expose: clear(), isEmpty(), toBase64()
  
  ใช้ signature_pad library
  Export เป็น PNG base64 string
-->
```

**Signature Flow ใน Step 3 (Guarantors):**
```
1. ผู้กู้กรอกข้อมูลผู้ค้ำประกัน (ชื่อ, รหัสสมาชิก, ตำแหน่ง)
2. ระบบแสดง UiSignaturePad สำหรับผู้ค้ำคนที่ 1
3. ผู้ค้ำวาดลายเซ็น → กด "ยืนยันลายเซ็น"
4. ระบบบันทึก base64 PNG ใน form state
5. (ถ้ามีผู้ค้ำคนที่ 2) ทำซ้ำ
6. ไป Step 4 สำหรับลายเซ็นผู้กู้
```

---

## 7.6 Auto-save Architecture

```typescript
// useAutoSave.ts
export function useAutoSave(draftId: Ref<string>, formStore: FormStore) {
  const DEBOUNCE_MS = 30_000  // 30 วินาที

  // Watch form data changes → debounce → API call
  watch(
    () => formStore.formData,
    debounce(async (newData) => {
      await draftService.save(draftId.value, {
        current_step: formStore.currentStep,
        form_data: newData
      })
    }, DEBOUNCE_MS),
    { deep: true }
  )
}
```

---

## 7.7 Route Structure & Guards

```typescript
// router/index.ts
const routes = [
  { path: '/login', component: LoginPage, meta: { requiresAuth: false } },
  
  // Borrower routes
  { path: '/dashboard', component: DashboardPage, meta: { requiresAuth: true } },
  { path: '/profile', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/apply', component: ApplicationPage, meta: { requiresAuth: true, role: 'borrower' } },
  { path: '/applications/:id', component: ApplicationDetailPage, meta: { requiresAuth: true } },
  
  // Staff routes (role guard)
  { path: '/staff', component: StaffDashboardPage, meta: { requiresAuth: true, role: 'staff' } },
  { path: '/staff/review/:id', component: ReviewPage, meta: { requiresAuth: true, role: 'staff' } },
  
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]

// Navigation Guard
router.beforeEach((to, from) => {
  const auth = useAuthStore()
  
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  
  if (to.meta.role && auth.user?.role !== to.meta.role) {
    return { path: '/dashboard' }  // redirect ไป dashboard ของ role ตัวเอง
  }
})
```

---

## 7.8 Dashboard Difference by Role

```
Borrower Dashboard                 Staff Dashboard
─────────────────                  ───────────────
- รายการคำขอของตัวเอง             - รายการคำขอทั้งหมด (filter/search)
- สถานะแต่ละคำขอ                  - คำขอที่รอ review (badge count)
- ปุ่ม "ยื่นคำขอใหม่"             - คำขอที่ review แล้ว (ประวัติ)
- Download PDF (ถ้า approved)     - Download PDF ของสมาชิกได้
                                   - ปุ่ม Approve / Reject
                                   - จัดการข้อมูลสมาชิก
```

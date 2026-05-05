# Sprint 5.5 — UI Architecture: Font, Theme, Component System, Pinia

**วันที่:** 2026-04-26  
**สถานะ:** ✅ COMPLETE

---

## สิ่งที่ทำในสปรินท์นี้

### 1. Font — Bai Jamjuree

| ไฟล์ | การเปลี่ยนแปลง |
|---|---|
| `index.html` | เปลี่ยน Google Fonts link จาก Sarabun → Bai Jamjuree (ครบ weight 200–700) |
| `src/assets/main.css` | `--font-sans: 'Bai Jamjuree', sans-serif` |

---

### 2. Theme Selector (32 DaisyUI v5 Themes)

**สิ่งที่สร้าง:**
- `src/stores/ui.store.ts` — เพิ่ม `theme`, `setTheme()`, `initTheme()` + persist ใน `localStorage` (key: `coopform-theme`)
- `src/components/ThemePicker.vue` — dropdown แสดง 32 themes พร้อม **color swatches จาก theme จริง** (`data-theme` on each row ทำให้ bg-primary/secondary/accent แสดงสีของ theme นั้น)
- `src/App.vue` — เรียก `ui.initTheme()` ตอน mount เพื่อ set `data-theme` บน `<html>`

**Themes ที่รองรับ:**
light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset

---

### 3. Component-Based Architecture

**หลักการ:** Pages บาง — แค่ orchestrate components / Components มี child components ได้

#### Component Tree

```
src/components/
├── ui/
│   └── UiInput.vue             ← primitive: label + input + optional error
├── AppLayout.vue               ← min-h-screen bg-base-200 + AppNavbar + <slot>
├── AppNavbar.vue               ← logo + ThemePicker + user dropdown (avatar, email, role, logout)
├── ThemePicker.vue             ← 32 themes + swatches
├── AddressFields.vue           ← 6 ช่องที่อยู่ (REUSED ใน ProfileEditCard AND Step1PersonalInfo)
│   └── UiInput (×6)
├── ProfileAccountCard.vue      ← ข้อมูลบัญชี read-only (อ่านจาก auth store โดยตรง)
├── ProfileEditCard.vue         ← v-model MemberProfileUpdate + save emit
│   ├── UiInput (×5)
│   └── AddressFields
├── DashboardActionCard.vue     ← card + title + description + action button (props-driven)
├── StatCard.vue                ← DaisyUI stat box (title, value, desc, valueClass)
├── LoginForm.vue               ← vee-validate + zod login form (ย้ายออกจาก LoginPage)
└── wizard/
    ├── FormWizard.vue          ← tabs + ใช้ formStore (ไม่มี local state)
    ├── Step1PersonalInfo.vue   ← UiInput (×5) + AddressFields
    ├── Step2LoanDetails.vue    ← input + select + คำนวณงวดเบื้องต้น
    ├── Step3Guarantors.vue     ← GuarantorForm (×2)
    └── GuarantorForm.vue       ← UiInput (×4) per guarantor
```

#### Pages (บาง)

| Page | Components ที่ใช้ |
|---|---|
| `LoginPage` | AppLayout (ไม่มี navbar) + `LoginForm` |
| `DashboardPage` | `AppLayout` + `DashboardActionCard` ×2 |
| `ProfilePage` | `AppLayout` + `ProfileAccountCard` + `ProfileEditCard` |
| `ApplicationPage` | `AppLayout` + `FormWizard` |
| `StaffDashboardPage` | `AppLayout` + `StatCard` ×3 |
| `ReviewPage` | `AppLayout` |

---

### 4. Pinia Store Redesign

#### `src/types/form.ts` (ใหม่)
Single source of truth สำหรับ form interfaces ทุก step:
- `Step1Data`, `Step2Data`, `GuarantorInfo`, `Step3Data`, `LoanOrdinaryFormData`
- ทั้ง store และ components import จากที่เดียวกัน (ไม่มี duplicate types)

#### `form.store.ts` (ออกแบบใหม่)

```
state:   draftId, formType, currentTab
         isDirty, saving, lastSaved, saveError
         step1 (reactive), step2 (reactive), step3 (reactive)
computed: formData → { step1, step2, step3 }
actions:  initFromDraft(draft)   ← โหลด draft จาก backend
          save()                 ← PUT /drafts/{id}
          markDirty()
          setTab(idx)
          updateStep1/2/3(data)  ← เรียกจาก FormWizard เมื่อ emit จาก step component
          reset()
auto-save: watch(isDirty) → setTimeout 30s → save()  ← ทำงานใน store เอง
```

**การไหลของข้อมูล (Form Wizard):**
```
draftService.createOrGet()
    → ApplicationPage → formStore.initFromDraft(draft)
                               ↓
                      FormWizard อ่าน formStore.step1/2/3
                      ส่งผ่าน :model-value ลง Step components (v-model, pure)
                      Step emit → FormWizard → formStore.updateStep1/2/3() + markDirty()
                      watch(isDirty) → 30s → formStore.save() → PUT /drafts
```

#### `profile.store.ts` (ใหม่)

```
state:   profile (MemberProfile | null), loading, saving, saved, error
computed: step1Prefill → Partial<Step1Data>  ← ใช้ pre-fill Step1 ใน Sprint 6
actions:  fetch(force?)   ← cache — ไม่โหลดซ้ำถ้ามีแล้ว
          update(data)    ← PUT /members/me/profile + update cache
          reset()
```

**การไหลของข้อมูล (Profile):**
```
onMounted → profileStore.fetch() → profile ref
watch(profile) → sync → form reactive (MemberProfileUpdate)
ProfileEditCard v-model ← form → @save → profileStore.update({ ...form })
```

---

### 5. แก้ Batch Files

**ปัญหา:** `set PYTHONUTF8=1` ใน CMD batch file อาจมี trailing space ทำให้ Python ปฏิเสธ

**แก้:** ใช้ `set "PYTHONUTF8=1"` (quotes รอบ name=value ป้องกัน trailing space)

ไฟล์ที่แก้: `start_backend.bat`, `start_dev.bat`

---

## ไฟล์ที่สร้าง / แก้ไข

### ใหม่
- `src/types/form.ts`
- `src/stores/profile.store.ts`
- `src/components/AppLayout.vue`
- `src/components/ui/UiInput.vue`
- `src/components/AddressFields.vue`
- `src/components/ProfileAccountCard.vue`
- `src/components/ProfileEditCard.vue`
- `src/components/DashboardActionCard.vue`
- `src/components/StatCard.vue`
- `src/components/LoginForm.vue`
- `src/components/wizard/GuarantorForm.vue`

### แก้ไข
- `src/stores/ui.store.ts` — theme system
- `src/stores/form.store.ts` — redesign ทั้งหมด
- `src/App.vue` — initTheme
- `index.html` — Bai Jamjuree font
- `src/assets/main.css` — font-sans
- `src/pages/LoginPage.vue` — ใช้ LoginForm
- `src/pages/DashboardPage.vue` — ใช้ AppLayout + DashboardActionCard
- `src/pages/ProfilePage.vue` — ใช้ AppLayout + profileStore + ProfileAccountCard + ProfileEditCard
- `src/pages/ApplicationPage.vue` — ใช้ AppLayout + formStore
- `src/pages/staff/StaffDashboardPage.vue` — ใช้ AppLayout + StatCard
- `src/pages/staff/ReviewPage.vue` — ใช้ AppLayout
- `src/components/wizard/FormWizard.vue` — ใช้ formStore (ไม่มี local state)
- `src/components/wizard/Step1PersonalInfo.vue` — import จาก @/types/form + ใช้ AddressFields
- `src/components/wizard/Step2LoanDetails.vue` — import จาก @/types/form
- `src/components/wizard/Step3Guarantors.vue` — import จาก @/types/form + ใช้ GuarantorForm
- `start_backend.bat`, `start_dev.bat` — แก้ PYTHONUTF8

---

## Sprint ถัดไป: Sprint 6 — Form Wizard Step 4–5

**เป้าหมาย:** Form ครบ 5 tabs + Pre-fill จาก profile

**งานที่ต้องทำ:**
1. `Step4Signatures.vue` — UiSignaturePad (signature_pad npm library)
2. `useSignature.ts` — lifecycle + base64 export
3. `Step5Review.vue` — สรุปข้อมูลทุก step ก่อน submit
4. Pre-fill Step1 จาก `profileStore.step1Prefill` (computed พร้อมแล้ว)
5. Zod validation schemas สำหรับ LoanOrdinaryFormData (ทุก step)
6. เพิ่ม Step4/5 ใน TABS registry ใน `FormWizard.vue`

**วิธีเพิ่ม tab:**
```typescript
// FormWizard.vue — TABS array
{ label: 'ลายเซ็น',  component: Step4Signatures },
{ label: 'ตรวจสอบ', component: Step5Review },
```

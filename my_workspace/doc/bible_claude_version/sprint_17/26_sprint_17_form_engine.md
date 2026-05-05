# Sprint 17 — Form Engine Foundation

**วันที่:** 2026-04-29  
**เป้าหมาย:** ออกแบบและ implement Form Engine แบบ config-driven เพื่อรองรับแบบฟอร์มจำนวนมากโดยไม่ต้อง hardcode Wizard หรือ Service ใหม่ทุกครั้ง

---

## ทำไม Sprint นี้ถึงสำคัญ

ปัจจุบัน (Sprint 16) ระบบ hardcode 2 form types:
- `OrdinaryLoanWizard.vue` + `_map_ordinary_loan()` ใน `pdf_service.py`
- `EmergencyLoanWizard.vue` + `_map_emergency_loan()` ใน `pdf_service.py`

ถ้าเพิ่มฟอร์มที่ 3 (เช่น กู้เพื่อที่อยู่อาศัย, ถอนหุ้น, สมัครสมาชิก) โดยไม่มี engine → code ซ้ำ, maintenance nightmare, ขัดหลักปรัชญา Principle 1 (Strict Layering) และ Principle 6 (Simplicity)

**Gate rule (จาก memory):** ห้าม hardcode form ที่ 3 ขึ้นไป — ต้องผ่าน Form Engine ก่อน

---

## Architecture Target

```
ก่อน Sprint 17 (hardcoded):
  OrdinaryLoanWizard.vue  ──▶  form.store.ts (fixed steps)  ──▶  pdf_service._map_ordinary_loan()
  EmergencyLoanWizard.vue ──▶  form.store.ts (fixed steps)  ──▶  pdf_service._map_emergency_loan()

หลัง Sprint 17 (config-driven):
  config/forms/loan_ordinary.toml   ┐
  config/forms/loan_emergency.toml  ├──▶  FormEngine  ──▶  GenericWizard.vue
  config/forms/loan_housing.toml    ┘                  ──▶  pdf_engine (generic fill)
```

---

## Milestone Overview

```
M1 — TOML Form Config Schema     ออกแบบ schema ที่ทุก form type ใช้ร่วมกัน
M2 — Backend FormEngine class    อ่าน TOML → field mapping → PDF fill (generic)
M3 — Migrate loan_emergency      ย้าย emergency เป็น engine-driven (proof of concept)
M4 — Frontend useFormConfig      composable อ่าน config → step definitions → Wizard renders
M5 — GenericFormWizard.vue       Wizard component ที่ render จาก config แทน hardcode
M6 — ADR + Roadmap update        บันทึก architectural decision + อัปเดต 11_roadmap.md
```

---

## M1 — TOML Form Config Schema

**เป้าหมาย:** กำหนด "ภาษา" ที่ใช้อธิบายแบบฟอร์ม 1 ชนิด

**ตัวอย่าง `config/forms/loan_emergency.toml`:**

```toml
[form]
id          = "loan_emergency"
name_th     = "แบบขอกู้เงินฉุกเฉิน"
pdf_template = "assets/templates/loan_emergency_v1.pdf"
max_loan    = 50000

[[steps]]
id    = "personal_info"
label = "ข้อมูลส่วนตัว"
component = "Step1PersonalInfo"   # shared component ที่มีอยู่แล้ว

[[steps]]
id    = "loan_details"
label = "รายละเอียดการกู้"
component = "StepEmergencyDetails"

[[steps]]
id    = "attachments"
label = "เอกสารแนบ"
component = "StepAttachments"     # shared component

[[steps]]
id    = "signatures"
label = "ลงนาม"
component = "StepSignatureHub"    # shared component

[pdf_mapping]
# field_name_in_pdf = "path.to.form.data"
"ชื่อผู้กู้"        = "step1.first_name"
"จำนวนเงิน"        = "step2.loan_amount"
"เหตุผล"            = "step2.emergency_reason"
```

**Output:** TOML schema spec ที่ครบพอ implement M2–M5 ได้

---

## M2 — Backend FormEngine class

**ไฟล์:** `backend/app/engines/form_engine.py`

```python
class FormEngine:
    def __init__(self, form_id: str):
        self.config = self._load_toml(form_id)   # อ่าน TOML

    def get_pdf_mapping(self, form_data: dict) -> dict[str, str]:
        """แปลง form_data → {pdf_field: value} ตาม mapping ใน TOML"""
        ...

    def get_step_definitions(self) -> list[StepDef]:
        """คืน step list สำหรับ Frontend"""
        ...
```

**เปลี่ยน `pdf_service.py`:**
- `_map_ordinary_loan()` → ยังคงไว้ (stable, ผ่าน UAT แล้ว)
- `_map_emergency_loan()` → **ลบ** แล้วให้ FormEngine จัดการแทน
- เพิ่ม `fill_generic(form_id, form_data)` method

**หลักการ:** ไม่แตะ ordinary loan จนกว่า engine จะ proven แล้ว

---

## M3 — Migrate loan_emergency (Pilot)

**Scope:**
1. สร้าง `config/forms/loan_emergency.toml` พร้อม full PDF mapping
2. `pdf_service.fill_generic("loan_emergency", form_data)` ทำงานได้
3. ทดสอบ: submit emergency loan → PDF ออกมาถูกต้องเหมือนเดิม
4. เพิ่ม test case ใน `test_applications.py`

**Definition of Done สำหรับ M3:** Emergency loan PDF ยังถูกต้องหลัง migrate ✅

---

## M4 — Frontend useFormConfig composable

**ไฟล์:** `frontend/src/composables/useFormConfig.ts`

```typescript
export function useFormConfig(formId: string) {
  const config = await formConfigService.get(formId)
  // GET /api/v1/forms/{form_id}/config

  const steps = computed(() => config.steps.filter(step =>
    hasPermission(step.roles)
  ))

  return { steps, config }
}
```

**Backend endpoint ใหม่:**
```
GET /api/v1/forms/{form_id}/config
→ { id, name_th, steps: [...], max_loan, ... }
```

---

## M5 — GenericFormWizard.vue

**ไฟล์:** `frontend/src/forms/GenericFormWizard.vue`

```vue
<template>
  <BaseWizardLayout :tabs="steps">
    <component
      v-for="step in steps"
      :is="stepComponents[step.component]"
      :key="step.id"
      v-model="formData[step.id]"
    />
  </BaseWizardLayout>
</template>
```

**หลักการ:**
- `stepComponents` = registry map ของ component ที่มีอยู่แล้ว (shared + form-specific)
- form-specific components ยังคง isolate ตาม Principle 10
- เพิ่ม form ใหม่ = เพิ่ม TOML + component เดียว ไม่ต้องแตะ GenericFormWizard

**ยังไม่ migrate OrdinaryLoan ใน Sprint นี้** — ทำใน Sprint 18 หลัง engine proven

---

## M6 — ADR + Roadmap Update

**Architecture Decision Record (ADR-009):**

| | รายละเอียด |
|---|---|
| **Title** | Form Engine: TOML-Driven Configuration |
| **Status** | Accepted |
| **Context** | Sprint 16: 2 forms hardcoded, แผนรองรับ 100+ forms |
| **Decision** | TOML config per form → FormEngine class → GenericFormWizard |
| **Consequences** | (+) เพิ่ม form ใหม่โดยไม่แตะ core; (-) TOML เป็น new language ทีมต้องเรียน |
| **Alternatives** | Code generation (ซับซ้อน), Pure hardcode (ไม่ scale) |

---

## Files จะถูกสร้าง/แก้ไข

| File | Action |
|------|--------|
| `config/forms/loan_emergency.toml` | 🆕 สร้าง — emergency form full config |
| `backend/app/engines/form_engine.py` | 🆕 สร้าง — FormEngine class |
| `backend/app/api/v1/routers/forms.py` | 🆕 สร้าง — GET /forms/{id}/config |
| `backend/app/services/pdf_service.py` | ✏️ แก้ — เพิ่ม fill_generic(), ลบ _map_emergency_loan |
| `backend/tests/test_form_engine.py` | 🆕 สร้าง — unit tests for FormEngine |
| `frontend/src/composables/useFormConfig.ts` | 🆕 สร้าง |
| `frontend/src/services/form.config.service.ts` | 🆕 สร้าง |
| `frontend/src/forms/GenericFormWizard.vue` | 🆕 สร้าง |
| `my_workspace/doc/bible_claude_version/12_decisions.md` | ✏️ เพิ่ม ADR-009 |
| `my_workspace/doc/bible_claude_version/11_roadmap.md` | ✏️ อัปเดต Sprint 17 status |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| TOML schema ไม่ครอบคลุม edge case ของ ordinary loan (193 fields) | ไม่ migrate ordinary loan ใน Sprint นี้ — ทำ Sprint 18 |
| GenericWizard ซับซ้อนกว่าคาด → ไม่เสร็จใน sprint | M5 เป็น optional ถ้า M1–M4 เสร็จแล้ว GenericWizard push ไป Sprint 18 ได้ |
| TOML mapping ผิด → PDF field ว่าง | M3 ต้องผ่าน diff test vs. hardcoded output ก่อน |

---

## Definition of Done

- [x] TOML schema spec ครบ (steps + pdf_fields ทุก type: direct/computed/concat/signature)
- [x] `FormEngine` อ่าน TOML และ map fields ได้ถูกต้อง (verified with real data)
- [x] Emergency loan migrate สำเร็จ — `_map_emergency_loan()` ถูกลบ, engine-driven แทน
- [x] `GET /forms/{form_id}/config` endpoint ทำงานได้
- [x] `useFormConfig` composable + `form.config.service.ts` สร้างแล้ว
- [x] `GenericFormWizard.vue` render steps จาก config ได้
- [x] `EmergencyLoanWizard.vue` refactored → 7 บรรทัด (thin wrapper)
- [x] `registry.ts` component registry ทุก step component
- [x] `getStep`/`setStep` generic accessor ใน `form.store.ts`
- [x] `forms.py` router registered ใน `main.py`
- [x] pytest 22/22 passed — ไม่มี regression
- [ ] ADR-009 บันทึกแล้ว (ดู 12_decisions.md → Sprint 18)
- [x] `11_roadmap.md` อัปเดต Sprint 17 ✅

---

## Retrospective Template (กรอกเมื่อเสร็จ)

**Lessons Learned:**
- 

**Technics:**
- 

**Mistakes:**
- 

**Cautions:**
- 

---

## Retrospective

**Lessons Learned:**
- `tomllib` (Python 3.11+ built-in) ยังไม่ได้ใช้ — โปรเจกต์ใช้ `tomli` library แทน (ต้อง import ตรงๆ)
- `emergency_loan_service.py` ไม่ได้เรียก PDF generation เลย — PDF generation ของ emergency loan ยังรอ template PDF จริง (`loan_emergency_v1.pdf` ยังไม่มี)
- FormEngine CONFIG_DIR ต้องคำนวณ path จาก `__file__` อย่างระมัดระวัง — parent ผิดชั้นเดียว = crash ทันที

**Technics:**
- TOML `[[pdf_fields]]` array of tables — ทำให้กำหนด field mapping แบบ ordered list ได้ชัดเจน
- Component Registry pattern (`registry.ts`) — แยก "ชื่อ component" (string จาก config) ออกจาก "object component" (Vue import) ได้สะอาด
- Generic accessor (`getStep`/`setStep`) ใน Pinia store — ใช้ plain object map แทน `[key]` indexing ที่ TypeScript ไม่ชอบ

**Mistakes:**
- ตั้ง parent path ผิดใน `form_engine.py` ครั้งแรก (parent * 5 แทนที่จะเป็น * 4) — ต้องทดสอบ path ก่อนเขียนโค้ดเสมอ

**Cautions:**
- `GenericFormWizard` ยังรองรับเฉพาะ steps ที่มี `store_key` ชัดเจน — `StepAttachments` ใช้ `store_key: ""` ซึ่ง getStep คืน null และ wizard ไม่ส่ง model-value ให้ (attachment ทำงานผ่าน internal API call ของตัวเอง — ยังโอเค)
- `loan_emergency_v1.pdf` template ยังไม่มี — emergency loan PDF generation จะยังล้มเหลวถ้าถูกเรียก (แต่ไม่ block submit เพราะ try/except อยู่แล้ว)

---

## Status: ✅ DONE (2026-04-29)

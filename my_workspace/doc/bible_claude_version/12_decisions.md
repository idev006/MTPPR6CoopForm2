# 12 — Architecture Decision Records (ADR)

> ADR บันทึก "ทำไม" ไม่ใช่แค่ "อะไร"  
> เพื่อให้คนที่เข้ามาทีหลัง (รวมถึงตัวเราเอง) เข้าใจว่าทำไมถึงตัดสินใจแบบนี้

---

## ADR-001: ใช้ pikepdf + reportlab แทน pypdf

**Status:** Accepted  
**วันที่:** 26 เมษายน 2568  
**ผู้ตัดสินใจ:** Project Team (จากผล Sprint 1)

### Context
ต้องการ library สำหรับกรอกข้อมูลลง AcroForm PDF ที่มี field ภาษาไทย

### Options Considered
1. `pypdf.update_page_form_field_values()` — pure Python, ง่าย
2. `pikepdf` + `reportlab` — ซับซ้อนกว่า, ต้องสร้าง appearance stream เอง
3. `pdfrw` + custom font — เก่า, community ไม่ active

### Decision
ใช้ **pikepdf + reportlab**

### Rationale
- `pypdf` พิสูจน์แล้วว่าไม่ทำงาน: field matching ล้มเหลวกับ dot-notation hierarchy, Thai font ออกเป็น □
- pikepdf navigate AcroForm hierarchy ได้ตรงตาม PDF spec
- reportlab สร้าง appearance stream ��ร้อม TTF font ได้ถูกต้อง 100%
- ผ่านการทดสอบจริง: 150 fields, 0 errors (Sprint 2)

### Consequences
- code ซับซ้อนกว่า pypdf (ต้องสร้าง appearance stream เอง)
- รองรับ Thai font, checkbox, signature ได้ครบ
- ต้องมี THSarabunNew.ttf อยู่บน server

---

## ADR-002: ไม่ใช้ Redis, Celery, MinIO

**Status:** Accepted  
**วันที่:** 26 เมษายน 2568

### Context
ระบบต้องการ: Auto-save Draft, PDF Generation, File Storage

### Options Considered
1. Redis (cache/queue) + Celery (task queue) + MinIO (object storage)
2. Database + Synchronous PDF gen + Local filesystem

### Decision
**Option 2** — Database + Synchronous + Filesystem

### Rationale
- Scale: 200 user, 30 req/hr — PDF gen < 3 วินาที → synchronous เพียงพอ
- 3 containers แทน 6+ containers — ลด complexity, ลด maintenance cost
- Backup ง่าย: `tar data/` + `pg_dump` — ไม่ต้องดูแล MinIO
- ถ้า scale เพิ่มในอนาคต สามารถเพิ่ม Redis + Celery + MinIO ได้โดยไม่ต้อง refactor logic หลัก (เพราะ PDF gen เป็น service แยก)

### Consequences
- PDF generation เป็น synchronous blocking call (รับได้ที่ scale นี้)
- ไฟล์ PDF อยู่บน host filesystem (ต้อง backup เองตามกำหนด)
- ถ้า scale เพิ่มขึ้นในอนาคต ต้องเพิ่ม async task queue

---

## ADR-003: Loose Coupling — Isolate Form Steps per Type

**Status:** Accepted  
**วันที่:** 26 เมษายน 2568

### Context
มีแบบฟอร์มหลายประเภท (กู้สามัญ, กู้ฉุกเฉิน, ...) บาง Step อาจดูคล้ายกัน

### Options Considered
1. **Generic Form Engine** — Step components ร่วมกัน, config-driven
2. **Per-type Isolation** — แต่ละ form type มี Step components เป็นของตัวเอง
3. **Hybrid** — Share UI primitives, Isolate business logic

### Decision
**Option 3 (Hybrid)** — Share UI Primitives, Isolate Form Steps

```
Share:   UiInput, UiSelect, UiButton, UiSignaturePad (no business logic)
Isolate: ordinary-loan/Step*.vue, emergency-loan/Step*.vue (แยกสมบูรณ์)
```

### Rationale
- แก้ validation rule ของ ordinary-loan ไม่กระทบ emergency-loan
- เพิ่ม form type ใหม่ = สร้าง folder ใหม่เท่านั้น
- Generic Form Engine ทำให้ debug ยาก, อ่านยาก, over-engineering สำหรับ scale นี้
- แม้จะมี code คล้ายกันใน 2 form types ก็ยอมรับได้ (better than tight coupling)

### Consequences
- อาจมี code duplication ระหว่าง form types
- แต่ละ form type อิสระสมบูรณ์ — ลบ/แก้ไขโดยไม่กังวล side effect

---

## ADR-004: form_data เก็บเป็น JSONB ใน PostgreSQL

**Status:** Accepted  
**วันที่:** 26 เมษายน 2568

### Context
แบบฟอร์มแต่ละประเภทมี fields ต่างกัน — จะเก็บข้อมูลอย่างไร?

### Options Considered
1. **One Table Per Form** — `ordinary_loan_data`, `emergency_loan_data`
2. **JSONB Column** — `form_data JSONB` ใน `loan_applications`
3. **EAV Pattern** — Entity-Attribute-Value (หนึ่ง row ต่อหนึ่ง field)

### Decision
**Option 2 — JSONB Column**

### Rationale
- รองรับหลาย form types โดยไม่ต้องเพิ่ม table
- PostgreSQL JSONB รองรับ indexing และ query ได้
- ไม่ต้องทำ schema migration ทุกครั้งที่ form เปลี่ยน
- Data ที่อ่านบ่อยที่สุด (application_no, status, amount) ยังคงเป็น typed columns
- EAV pattern ซับซ้อนเกินไปสำหรับ scale นี้

### Consequences
- Query ลง JSONB field ซับซ้อนกว่า typed column
- ต้องระวัง schema ของ JSONB เอง (Pydantic validate ก่อน save)
- Migration ข้อมูลใน JSONB ยากกว่า typed column

---

## ADR-005: JWT เก็บใน Memory + HttpOnly Cookie (ไม่ใช้ localStorage)

**Status:** Accepted  
**วันที่:** 26 เมษายน 2568

### Context
SPA ต้องการเก็บ JWT token ไว้ใช้งาน — จะเก็บที่ไหน?

### Options Considered
1. **localStorage** — ง่าย, อยู่รอดหลัง refresh
2. **Memory (Pinia store)** — ปลอดภัยกว่า, หายเมื่อ refresh
3. **HttpOnly Cookie** — ปลอดภัยสูงสุด, ส่งอัตโนมัติ แต่ CSRF risk

### Decision
**Access Token = Memory, Refresh Token = HttpOnly Cookie**

### Rationale
- localStorage เสี่ยง XSS อ่านได้
- Access token อยู่ใน memory — อ่านจาก JS ได้ แต่ XSS ก็อ่านได้เช่นกัน
- Refresh token อยู่ใน HttpOnly Cookie — JS อ่านไม่ได้, ส่งอัตโนมัติ
- เมื่อ refresh browser → access token หาย → ใช้ refresh token ต่ออัตโนมัติ
- Pattern นี้เป็น industry standard สำหรับ SPA

### Consequences
- ต้อง implement auto-refresh interceptor ใน Axios
- Refresh token ใน Cookie ต้องการ SameSite=Strict ป้องกัน CSRF

---

## ADR-006: Draft Cleanup ด้วย FastAPI Lifespan (ไม่ใช้ Celery)

**Status:** Accepted  
**วันที่:** 26 เมษายน 2568

### Context
DRAFT_SESSIONS มี expires_at — ต้องมีกลไกลบ draft ที่หมดอายุ

### Options Considered
1. **Celery beat** — schedule task
2. **FastAPI lifespan** — cleanup เมื่อ server start
3. **Lazy delete** — ลบเมื่อ user login
4. **pg_cron** — PostgreSQL extension

### Decision
**FastAPI lifespan + Lazy delete**

### Rationale
- ไม่มี Celery ในระบบ (ADR-002)
- Lifespan cleanup เพียงพอสำหรับ 200 users, draft expire 30 วัน
- Lazy delete ใน `GET /drafts/{form_type}` เป็น safety net
- pg_cron ต้องติดตั้ง extension เพิ่ม — ซับซ้อนเกินความจำเป็น

### Consequences
- Draft ถูกลบเมื่อ server restart เท่านั้น (ยอมรับได้)
- ถ้า server ไม่ restart นาน → expired drafts อยู่ใน DB (ไม่กระทบ functionality)

---

## ADR-008: StepAttachments.vue — Known Architecture Violation (Tech Debt)

**Status:** Tech Debt — Planned Fix Sprint 11  
**วันที่ตรวจพบ:** 28 เมษายน 2568  
**ผู้ตรวจพบ:** Audit Session

### Context
`StepAttachments.vue` (ใน `src/forms/shared/`) เรียก `api.post()`, `api.get()`, `api.delete()` โดยตรงจากภายใน component ซึ่งละเมิด:
- §1 Strict Layering — Component ไม่ควรยุ่งกับ HTTP layer โดยตรง
- §11.3 Service Layer Contract — "❌ Component เรียก api.post() โดยตรง"

### Why It Happened
Sprint 9 implement attachment system ก่อนที่ §11 Component Communication Architecture จะถูกเพิ่มเข้า `00_design_philosophy.md` (ซึ่งเพิ่มใน Sprint 10) ทำให้ไม่มีกฎที่ชัดเจน ณ เวลาที่ code ถูกเขียน

### Options Considered
1. **ปล่อยไว้ (Current)** — ทำงานได้ แต่ผิด pattern, ทดสอบยาก
2. **สร้าง `attachment.service.ts`** — ย้าย HTTP calls ออก, component emit event → store เรียก service

### Decision
**Option 2** — แก้ใน Sprint 11 โดย:
```
❌ ปัจจุบัน: StepAttachments.vue → api.post('/attachments/...')
✅ เป้าหมาย: StepAttachments.vue emit('upload', file)
              → form.store / page เรียก attachmentService.upload(file)
              → attachmentService → api.post(...)
```

### Rationale
- ตรง pattern ใน `00_design_philosophy.md` §11.3
- Error handling และ loading state ไปรวมอยู่ที่ Store
- Unit test ทำได้โดย mock `attachmentService` แทน mock axios

### Consequences (ชั่วคราว ก่อนแก้)
- StepAttachments.vue ไม่สามารถ unit test ได้อย่างถูกต้อง
- Error state กระจายอยู่ใน component แทนที่จะเป็น centralized store
- ไม่มีผลต่อ production functionality — ระบบทำงานปกติ

---

## ADR-007: PostgreSQL สำหรับ Production (ไม่ใช้ SQLite)

**Status:** Accepted  
**วันที่:** 26 เมษายน 2568

### Context
เลือก database สำหรับ production ระหว่าง SQLite และ PostgreSQL

### Decision
**PostgreSQL 16** สำหรับ Production, SQLite สำหรับ Dev testing เท่านั้น

### Rationale
- JSONB native ใน PostgreSQL — ต้องการสำหรับ form_data, guarantors
- ACID transactions — สำคัญสำหรับ submit flow (create application + generate PDF + delete draft)
- Concurrent access ดีกว่า SQLite มาก (แม้ scale เล็ก)
- SQLAlchemy + Alembic รองรับทั้งคู่ — switch ง่าย

### Consequences
- ต้องมี PostgreSQL container (เพิ่ม docker-compose 1 service)
- Backup ต้องใช้ pg_dump (ซับซ้อนกว่า copy file เดียวของ SQLite)

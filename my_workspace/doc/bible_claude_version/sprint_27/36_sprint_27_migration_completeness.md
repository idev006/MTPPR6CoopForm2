# Sprint 27 — Migration Completeness + PostgreSQL Readiness

**วันที่:** 2026-05-03
**สถานะ:** ✅ DONE

---

## ปัญหาที่พบ (Root Cause Analysis)

Dev database (SQLite) ใช้งานได้ปกติเพราะ test conftest.py ใช้ `Base.metadata.create_all()` สร้างตารางทั้งหมดจาก models
แต่ **Alembic migrations ไม่ครบ** — ถ้า deploy บน PostgreSQL ใหม่แล้ว `alembic upgrade head` จะได้ตารางไม่ครบ

### Gap Analysis

| ตาราง | สร้างโดย migration? | สร้างโดย create_all? | สถานะ |
|---|---|---|---|
| `users` | ✅ 001 | ✅ | OK |
| `member_profiles` | ✅ 001 | ✅ | OK |
| `loan_applications` | ✅ 002 | ✅ | OK |
| `draft_sessions` | ✅ 002 | ✅ | OK |
| `generated_pdfs` | ✅ 002 | ✅ | OK |
| `attachments` | ✅ 002 (มี FK ผิด) | ✅ (ไม่มี FK) | ⚠️ FK ต้องแก้ |
| `audit_logs` | ✅ 002 | ✅ | OK |
| `application_parties` | ❌ **ขาด** | ✅ | 🔴 MISSING |
| `signatures` | ❌ **ขาด** | ✅ | 🔴 MISSING |
| `notifications` | ❌ **ขาด** | ✅ | 🔴 MISSING |
| `loan_applications.cancelled_at` | ✅ 006 | ✅ | OK |
| `loan_applications.cancel_reason` | ✅ 006 | ✅ | OK |

### Bug: FK บน attachments.application_id

Migration 002 สร้าง:
```python
sa.Column("application_id", sa.Uuid(), sa.ForeignKey("loan_applications.id", ondelete="CASCADE"))
```

แต่ระบบ upload attachment ช่วง **draft phase** ใช้ `application_id = draft_session_id` — ซึ่งเป็น UUID ของ `draft_sessions` ไม่ใช่ `loan_applications`

- **SQLite**: FK ไม่ enforce → ใช้งานได้ใน dev (ไม่เห็นปัญหา)
- **PostgreSQL**: FK enforce → INSERT attachment ช่วง draft จะ **FK violation error** ทันที

Model ปัจจุบัน (`attachment.py`) ไม่มี FK (แก้ไว้แล้วใน model) แต่ migration 002 ยังสร้าง FK อยู่

### Bug: postgresql.UUID ใน models

`application_party.py` และ `signature.py` ใช้:
```python
from sqlalchemy.dialects.postgresql import UUID
id = Column(UUID(as_uuid=True), ...)
```

ขัดกับ Key Decision: **"Models ใช้ sa.Uuid + sa.JSON (generic)"**

---

## เป้าหมาย

ทำให้ `alembic upgrade head` บน PostgreSQL ใหม่ สร้างตารางครบ 100% ถูกต้องทุกตาราง

---

## Migration Chain (เป้าหมาย)

```
001 (users, member_profiles)
  └─ 002 (loan_applications, drafts, generated_pdfs, attachments, audit_logs)
       └─ 003 (fix attachments FK — drop FK บน application_id)
            └─ 004 (application_parties, signatures)
                 └─ 005 (notifications)
                      └─ 006 (loan_applications.cancelled_at + cancel_reason)
```

---

## Tasks

### A — Migration 003: Fix Attachments FK
- Drop FK constraint `attachments_application_id_fkey`
- ใช้ `batch_alter_table` เพื่อ SQLite compat
- หลังจากนี้ `application_id` เป็น bare UUID (ชี้ไปได้ทั้ง draft_session หรือ loan_application)

### B — Migration 004: application_parties + signatures
- สร้างตาราง `application_parties` (ใช้ `sa.Uuid` แทน `postgresql.UUID`)
- สร้างตาราง `signatures` (ใช้ `sa.Uuid`)

### C — Migration 005: notifications
- สร้างตาราง `notifications`

### D — Update migration 006
- เปลี่ยน `down_revision = "002"` → `down_revision = "005"`

### E — Fix models
- `application_party.py`: `postgresql.UUID` → `Mapped[uuid.UUID] = mapped_column(Uuid, ...)`
- `signature.py`: `postgresql.UUID` → `Mapped[...] = mapped_column(Uuid, ...)`

---

## Design Decisions

### D-1: ใช้ batch_alter_table ใน migration 003
SQLite ไม่รองรับ `ALTER TABLE DROP CONSTRAINT` โดยตรง
`batch_alter_table` ให้ Alembic recreate ตาราง + index ใหม่โดยไม่มี FK — ใช้ได้ทั้ง SQLite + PostgreSQL

### D-2: ไม่เพิ่ม draft_id column ใน attachments
ระบบปัจจุบันใช้ `application_id` เพื่อเก็บทั้ง `draft_id` และ `loan_application_id`
แล้วทำ UPDATE ที่ submit time — วิธีนี้ใช้งานได้และไม่จำเป็นต้องแยก column

### D-3: Dev SQLite ไม่ต้อง re-run migrations
Dev DB ที่ alembic_version = "006" ใช้งานได้ต่อไปได้เลย เพราะ:
- ตาราง application_parties, signatures, notifications มีอยู่แล้ว (สร้างโดย create_all)
- `alembic upgrade head` จะเห็นว่า "already at 006 (head)" — ไม่ทำอะไร
- ไม่ต้อง stamp หรือ fake apply

### D-4: Rewrite application_party.py + signature.py เป็น Mapped[] style
สอดคล้องกับ models อื่นที่ใช้ SQLAlchemy 2.0 Mapped syntax
ใช้ `sa.Uuid` (generic) แทน `postgresql.UUID` — cross-DB compat

---

## Bonus Fix (พบระหว่าง coding)

### B-1: cancel endpoint body optional
`POST /applications/{id}/cancel` ใช้ `body: CancelRequest` (required) ทำให้ test ที่ไม่ส่ง body ได้ 422
แก้เป็น `body: Optional[CancelRequest] = Body(default=None)` และ `reason = body.reason if body else None`
Frontend ที่ส่ง `{ reason: "..." }` ยังทำงานได้เหมือนเดิม

---

## Definition of Done

- [x] A: migration 003 สร้างได้ + ทดสอบบน SQLite (batch_alter_table recreate="always")
- [x] B: migration 004 สร้าง application_parties + signatures ถูกต้อง
- [x] C: migration 005 สร้าง notifications ถูกต้อง
- [x] D: migration 006 down_revision อัปเดตแล้ว (002 → 005)
- [x] E: application_party.py + signature.py ใช้ sa.Uuid + Mapped[] style แล้ว
- [x] F: `alembic upgrade head` บน fresh SQLite ผ่าน — ได้ครบ 10 ตาราง
- [x] G: pytest 22/22 passed (รวม bonus fix B-1)

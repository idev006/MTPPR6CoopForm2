# Sprint 26 — Cancel Application Enhancement

**วันที่:** 2026-04-30
**สถานะ:** ✅ DONE

---

## เป้าหมาย

ปรับปรุง flow การยกเลิกคำขอกู้ให้สมบูรณ์ครบวงจร:
- ผู้กู้ระบุเหตุผลการยกเลิกได้
- Staff รับการแจ้งเตือนทันทีเมื่อมีการยกเลิก (ไม่ต้องรอตรวจคำขอที่ไม่มีอยู่)
- บันทึก audit trail อย่างถูกต้อง (`cancelled_at`, `cancel_reason`)
- UI แสดงสถานะและจัดกลุ่มรายการให้ชัดเจน

---

## หลักการ: Cancelled ≠ Draft Delete

| | ร่างคำขอ (Draft) | คำขอที่ยกเลิก (Cancelled) |
|---|---|---|
| เลขคำขอ | ไม่มี | มี (ORD-26-XXXX) |
| Staff รับทราบแล้ว | ไม่ | **ใช่** |
| ลบ record ได้ | ✅ | ❌ Soft-delete เท่านั้น |
| ลบ Attachments | ✅ | ❌ เก็บไว้เป็นหลักฐาน |
| ลบ PDF | ✅ | ❌ เก็บไว้ |
| Audit requirement | ต่ำ | **สูง** |

---

## Sequence Diagram

```
┌──────────┐  ┌──────────────────┐  ┌──────────────┐  ┌─────────┐
│ Borrower │  │ApplicationDetail │  │  Backend     │  │  Staff  │
└────┬─────┘  └────────┬─────────┘  └──────┬───────┘  └────┬────┘
     │                 │                   │               │
     │──กด ยกเลิกคำขอ─▶│                   │               │
     │                 │                   │               │
     │       ┌─────────▼──────────────┐    │               │
     │       │  Cancel Modal          │    │               │
     │       │  [textarea เหตุผล]     │    │               │
     │       │  [ยืนยัน] [ปิด]        │    │               │
     │       └─────────┬──────────────┘    │               │
     │                 │                   │               │
     │──ยืนยัน+เหตุผล──▶│                   │               │
     │                 │─POST /cancel──────▶│               │
     │                 │ { reason }        │               │
     │                 │                   │               │
     │                 │          ┌────────▼─────────────────────────┐
     │                 │          │ 1. verify status == "submitted"  │
     │                 │          │ 2. app.status     = "cancelled"  │
     │                 │          │ 3. app.cancelled_at = now()      │
     │                 │          │ 4. app.cancel_reason = reason    │
     │                 │          │ 5. AuditLog: action="CANCEL"     │
     │                 │          │ 6. notify_staff_cancel()         │
     │                 │          └────────┬─────────────────────────┘
     │                 │◀── 200 ───────────│               │
     │                 │                   │               │
     │                 │  ┌────────────────▼────────────┐  │
     │                 │  │ UI update:                  │  │
     │                 │  │ - badge "ยกเลิกแล้ว"        │  │
     │                 │  │ - ซ่อนปุ่มทุกปุ่ม action    │  │
     │                 │  │ - แสดง cancel_reason+date   │  │
     │                 │  └─────────────────────────────┘  │
     │                 │                   │               │
     │                 │                   │──Notification─▶│
     │                 │                   │ "ผู้กู้ [ชื่อ]  │
     │                 │                   │  ยกเลิกคำขอ  │
     │                 │                   │  ORD-26-XXXX" │
```

---

## Gap Analysis (สิ่งที่ขาด)

| # | Gap | Priority |
|---|---|---|
| G-1 | ไม่แจ้ง Staff เมื่อผู้กู้ยกเลิก | 🔴 High |
| G-2 | ไม่มีช่อง cancel_reason | 🟡 Medium |
| G-3 | ไม่มี cancelled_at timestamp | 🟡 Medium |
| G-4 | Staff กรอง/ดู cancelled ไม่ได้ | 🟡 Medium |
| G-5 | Dashboard ผสม cancelled กับ active | 🟡 Medium |
| G-6 | ApplicationDetailPage แสดงปุ่ม action แม้ cancelled | 🟢 Low |

---

## Tasks

### A — Database Migration
- เพิ่ม column `cancelled_at TIMESTAMP WITH TIME ZONE NULL`
- เพิ่ม column `cancel_reason TEXT NULL` (max 500 chars ใน validation)
- สร้าง Alembic migration `006_cancel_fields`

### B — Backend: อัปเดต cancel endpoint
- รับ `CancelRequest` schema: `{ reason: Optional[str] }`
- set `cancelled_at = datetime.now(utc)`, `cancel_reason = reason`
- เพิ่ม `AuditLog` entry: `action="CANCEL"`, `new_values={status, reason}`
- เรียก `NotificationService` แจ้ง staff ทุกคน

### C — Frontend: ApplicationDetailPage
- Cancel Modal: เพิ่ม `<textarea>` เหตุผล (optional, max 500)
- ส่ง `{ reason }` ไปกับ POST cancel
- ซ่อนปุ่ม "ยกเลิกคำขอ" และ "ส่งเอกสารเพิ่มเติม" เมื่อ status = cancelled
- แสดง section "เหตุผลการยกเลิก" + `cancelled_at`

### D — Frontend: DashboardPage
- แยก applications เป็น 2 กลุ่ม:
  - **Active**: submitted | under_review | pending_documents | approved
  - **ปิดแล้ว**: cancelled | rejected — แสดงแบบ collapsible (ค่าเริ่มต้น: ปิด)

### E — Frontend: Staff Navigation + Page
- เพิ่ม nav item "ยกเลิกแล้ว" ใน `navigation.ts` (ไม่มี badge count)
- Staff page รองรับ `?status=cancelled` filter แล้ว (ใช้ endpoint เดิม)

---

## Schema Changes

```python
# LoanApplication model — เพิ่ม 2 fields
cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
cancel_reason: Mapped[str | None] = mapped_column(Text)
```

```python
# CancelRequest schema (ใหม่)
class CancelRequest(BaseModel):
    reason: Optional[str] = None

    @field_validator('reason')
    def reason_max_length(cls, v):
        if v and len(v) > 500:
            raise ValueError('เหตุผลต้องไม่เกิน 500 ตัวอักษร')
        return v
```

---

## Navigation Config เพิ่ม

```typescript
// Staff nav — เพิ่ม cancelled item (ไม่มี badge)
{ type: 'item', label: 'ยกเลิกแล้ว', path: '/staff?status=cancelled',
  icon: '🚫', roles: [ROLES.STAFF] }
```

---

## Definition of Done

- [x] A: Alembic migration `006_cancel_fields` รัน apply สำเร็จ
- [x] B: `POST /applications/{id}/cancel` บันทึก reason + cancelled_at + AuditLog + Notification
- [x] C: Cancel Modal มี textarea, แสดง cancel info, ซ่อน action buttons
- [x] D: DashboardPage แยก active/ปิดแล้ว (collapsible)
- [x] E: Staff sidebar มี "ยกเลิกแล้ว" link, กรองได้

---

## Design Decisions

### D-1: เก็บข้อมูลทั้งหมดเมื่อยกเลิก (ไม่ลบ)
Cancelled application มีเลขคำขอทางการ ถูก staff รับแล้ว
→ ต้องเก็บ audit trail ครบ: record + attachments + PDF + parties

### D-2: cancel_reason เป็น Optional
ผู้กู้อาจยกเลิกโดยไม่ต้องให้เหตุผล (เช่น เปลี่ยนใจ)
แต่ถ้าให้เหตุผล staff เห็นได้ใน ApplicationDetail

### D-3: Dashboard แยก active / ปิดแล้ว (collapsed)
cancelled + rejected อยู่กลุ่มเดียวกัน เพราะทั้งคู่เป็น "จบแล้ว"
collapsed by default เพื่อไม่รบกวน UX หลัก

### D-4: Staff Notification เมื่อยกเลิก
เพื่อให้ staff ไม่ต้องเปิดคำขอที่ถูกยกเลิกไปแล้ว
ใช้รูปแบบเดียวกับ `_notify_staff_new_application`

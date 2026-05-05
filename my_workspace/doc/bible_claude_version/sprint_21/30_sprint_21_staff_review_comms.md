# Sprint 21 — Staff Review Redesign & Borrower-Staff Communication

**วันที่:** 2026-04-30  
**สถานะ:** ✅ DONE

---

## เป้าหมาย

1. Staff Review Page: ออกแบบใหม่ให้ตรวจสอบเอกสารได้จริง (เสมือนตรวจกระดาษ)
2. เพิ่มสถานะ `pending_documents` — Staff ขอเอกสารเพิ่มจาก Borrower
3. Bidirectional Communication: ทั้งสองฝ่ายได้รับ notification ที่ "ต้องรู้" ครบถ้วน

---

## Communication Matrix (สิ่งที่ออกแบบ)

| Event | ผู้ส่ง | ผู้รับ | เนื้อหา | ประเภท |
|-------|--------|--------|---------|--------|
| ยื่นคำขอใหม่ | Borrower | Staff ทุกคน | "คำขอกู้สามัญใหม่ — {เลขที่}, ผู้กู้: {ชื่อ}, ยอด: {บาท}" | info |
| เปลี่ยนสถานะ: under_review | Staff | Borrower | "คำขอ {เลขที่} อยู่ระหว่างการพิจารณาของเจ้าหน้าที่" | info |
| เปลี่ยนสถานะ: pending_documents | Staff | Borrower | "เจ้าหน้าที่ขอเอกสารเพิ่ม — {หมายเหตุ}" | warning |
| เปลี่ยนสถานะ: approved | Staff | Borrower | "คำขอ {เลขที่} ได้รับการอนุมัติแล้ว" | success |
| เปลี่ยนสถานะ: rejected | Staff | Borrower | "คำขอ {เลขที่} ถูกปฏิเสธ — {หมายเหตุ}" | error |

**Notification link:**
- Staff ← `/staff/applications/{id}` (คลิกไปหน้า ReviewPage ทันที)
- Borrower ← `/applications/{id}` (คลิกไปหน้า ApplicationDetailPage)

---

## Sequential Diagram (Borrower → Staff)

```
Borrower                  Frontend                Backend                 DB
   │── ยื่นคำขอ ───────────>│                       │                     │
   │   (submit)              │── POST /applications ─>│                     │
   │                         │                       │── INSERT app ────────>│
   │                         │                       │── notify ALL staff ──>│ (notifications)
   │                         │<─ 201 { app_no } ─────│                     │
   │<── Success Modal ────────│                       │                     │
   │                         │                       │                     │
Staff                   NotificationBell         Backend                  DB
   │ (poll ทุก 30 วิ) ───────>│                       │                     │
   │                         │── GET /notifications ─>│                     │
   │                         │<─ [{ title, link }] ──│                     │
   │<── Badge แดง (1 ใหม่) ──│                       │                     │
   │── คลิก notification ────>│── router.push(link) ──>│                     │
   │<── ReviewPage โหลด ─────│                       │                     │
   │                         │                       │                     │
   │── ตัดสินใจ + กด ─────────>│── PATCH /review ──────>│── UPDATE status ─────>│
   │   (pending_docs)        │                       │── notify Borrower ───>│ (notifications)
   │                         │                       │                     │
Borrower                NotificationBell                                   │
   │ (poll ทุก 60 วิ) ───────>│── GET /notifications ─>│                     │
   │<── Badge แดง + alert ───│                       │                     │
   │── คลิก notification ────>│── router.push(/apps/id)│                     │
   │<── ApplicationDetailPage│                       │                     │
   │   "รอเอกสารเพิ่มเติม"  │                       │                     │
   │   + หมายเหตุ staff      │                       │                     │
```

---

## สิ่งที่สร้าง / แก้ไข

### Backend

#### `app/schemas/application_review.py`
- `ReviewRequest.status` เพิ่ม `pending_documents` ใน pattern
- `ApplicationStaffListItem.requested_amount` → `Optional[float]`
- เพิ่ม `AttachmentSchema` (id, file_type, original_filename, mime_type, uploaded_at)
- `ApplicationStaffDetail` เพิ่ม: `reviewed_at`, `review_remarks`, `attachments: List[AttachmentSchema]`

#### `app/services/review_service.py`
- `get_applications_for_staff(status=None)` — รองรับ status filter
- `get_application_detail()` — รวม `attachments[]` จาก DB + `reviewed_at`, `review_remarks`
- `update_status()` — `STATUS_CONFIG` dict ครบ 4 สถานะ, message template แยก context ชัดเจน, รวม remarks ใน message ถ้ามี
- Import `Attachment` model

#### `app/api/v1/routers/staff_applications.py`
- `GET /staff/applications` รับ `?status=` query param (validated pattern)
- Import `Query`, `Optional`, `StreamingResponse`

#### `app/services/application_service.py`
- Import `NotificationService`
- `submit_ordinary_loan()` เรียก `_notify_staff_new_application()` หลัง commit
- `_notify_staff_new_application()`: query `User.role == "staff"` → notify ทุกคน
  - link = `/staff/applications/{app.id}`
  - Notification failure ไม่ทำให้ submission fail (try/except with logger.warning)

---

### Frontend

#### `src/services/staff.service.ts` (เขียนใหม่)
```typescript
type ReviewStatus = 'approved' | 'rejected' | 'under_review' | 'pending_documents'

staffService.getApplications(status?: string)       // query param
staffService.getApplicationDetail(id)               // returns ApplicationDetail with attachments[]
staffService.reviewApplication(id, { status, remarks })
staffService.openPdf(appId)                         // axios blob → createObjectURL → window.open
staffService.openAttachment(attachmentId)            // axios blob → createObjectURL → window.open
```

#### `src/pages/staff/ReviewPage.vue` (redesign ใหม่)
- Layout: 2 columns (xl: 3/5 + 2/5)
- **คอลัมน์ซ้าย:**
  - Header card: application_no, status badge, review_remarks ถ้ามี
  - Borrower Info: ชื่อ, รหัสสมาชิก, บัตรประชาชน, ตำแหน่ง, สังกัด, โทร, สถานะสมรส, คู่สมรส
  - Loan Details: ยอดเงินกู้ (ตัวใหญ่สีน้ำเงิน), งวด, ช่องทางรับเงิน, วัตถุประสงค์, ธนาคาร/เลขบัญชี
  - Guarantors: loop ทุกคน แสดงข้อมูลครบ (name, member_code, id_card, position, department, marital)
- **คอลัมน์ขวา:**
  - PDF viewer button (blob URL via `staffService.openPdf`)
  - Attachment list: loop `app.attachments[]`, label ด้วย `DOC_LABEL[file_type]`, ปุ่ม "ดู" ต่อไฟล์ (blob URL)
  - Signature list จาก `app.parties[]`
  - Decision panel: 4 ปุ่ม (อนุมัติ / ขอเอกสารเพิ่ม / ปฏิเสธ / กำลังตรวจสอบ) — ซ่อนเมื่อ finalized
- **Decision Modal (DaisyUI `<dialog>`):**
  - remarks textarea: required สำหรับ `rejected` + `pending_documents`, optional สำหรับอื่น
  - `canConfirm` computed ป้องกัน submit ก่อนกรอก remarks
  - แต่ละ status ใช้ btn class ต่างกัน (success/warning/error/info)
  - submit → `router.push('/staff')` เมื่อสำเร็จ

#### `src/pages/staff/StaffDashboardPage.vue` (อัปเดต)
- เพิ่ม Filter Tabs: ทั้งหมด / รอดำเนินการ / กำลังตรวจสอบ / รอเอกสารเพิ่ม / อนุมัติแล้ว / ปฏิเสธ
- `watch(activeTab, () => loadApplications())` — re-fetch เมื่อ tab เปลี่ยน
- `getApplications(status?)` ส่ง query param ไป backend
- `pending_documents` ใน STATUS_LABEL + STATUS_CLASS

#### `src/pages/ApplicationDetailPage.vue` (อัปเดต)
- `statusLabel['pending_documents'] = 'รอเอกสารเพิ่มเติม'`
- `statusClass['pending_documents'] = 'badge-warning'`
- Alert banner สีเหลือง: แสดงเมื่อ `status === 'pending_documents'` พร้อม `review_remarks`
- Timeline: เพิ่ม step "รอเอกสารเพิ่ม" (warning color) แทน "อนุมัติ" เมื่อ status นั้น
- `review_remarks` แสดงใน timeline section เมื่อ approved/rejected

#### `src/components/layout/NotificationBell.vue` (อัปเดต)
- Poll interval: `staff → 30,000ms`, `borrower → 60,000ms`
- `onUnmounted(() => clearInterval(timer))` — ป้องกัน memory leak
- Click-outside overlay (full-screen `div` z-40)
- Type dot: แต่ละสี per `notif.type` (success/error/warning/info)
- Type badge: แสดง label สั้น (อนุมัติ / ไม่อนุมัติ / แจ้งเตือน / ข้อมูล) ต่อ notification
- `9+` cap เมื่อ unreadCount > 9

---

## Design Decisions

### D-1: Notification failure ≠ Submission failure
```python
try:
    await self._notify_staff_new_application(...)
except Exception as e:
    logger.warning(f"Staff notification failed: {e}")  # ไม่ throw
```
เหตุผล: notification เป็น "nice-to-have" — submission ต้องไม่ fail เพราะ notification ล้มเหลว

### D-2: Staff poll 30s, Borrower poll 60s
Staff ต้องรู้ทันทีเมื่อมีคำขอใหม่ (workflow เร็ว), Borrower รอได้นานกว่า

### D-3: remarks required เฉพาะ rejected + pending_documents
- `approved`: staff ไม่ต้องอธิบาย (เป็น positive action)
- `under_review`: เป็น interim state, ไม่ต้องมีคำอธิบาย
- `rejected`: Borrower ต้องรู้ว่าทำไม
- `pending_documents`: Borrower ต้องรู้ว่าต้องส่งอะไรเพิ่ม

### D-4: PDF + Attachments ใช้ axios blob แทน `window.open(URL)` ตรง
เหตุผล: ทุก endpoint ต้องการ Authorization header — `window.open` ไม่ส่ง header → 401
Pattern: `axios.get(url, {responseType: 'blob'}) → URL.createObjectURL() → window.open(blobUrl)`

---

## Tests

Regression เดิม: pytest 22/22 ✅ (ไม่มี regression จากการเพิ่ม notify)

---

## Pending (ไม่ใช่ส่วนหนึ่งของ Sprint นี้)

- WebSocket / SSE สำหรับ real-time notification (แทน polling) — Backlog
- Email / LINE Notify integration — Backlog
- ปุ่ม "ส่งเอกสารเพิ่ม" บนหน้า Borrower เมื่อ `pending_documents` — Sprint ถัดไป

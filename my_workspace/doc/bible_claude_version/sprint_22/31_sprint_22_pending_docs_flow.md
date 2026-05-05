# Sprint 22 — Complete pending_documents Flow

**วันที่:** 2026-04-30  
**สถานะ:** ✅ DONE  
**pytest:** 22/22 passed ✅

---

## เป้าหมาย

ปิด gap ใน `pending_documents` flow — ก่อนหน้านี้ borrower เห็น banner แต่ทำอะไรไม่ได้
หลัง Sprint นี้ flow สมบูรณ์ end-to-end:

```
Staff: pending_documents + remarks
  → Borrower: เห็น banner + หมายเหตุ staff
  → Borrower: อัปโหลดเอกสารเพิ่มทีละไฟล์ (ระบุประเภท)
  → Borrower: กด "ยืนยันส่งเอกสารเพิ่มเติม"
  → System: status → submitted + notify staff
  → Staff: notification bell + link ไป ReviewPage
  → Staff: เห็น attachments ใหม่ใน right column
  → Staff: ตัดสินใจรอบสอง (approved / rejected / pending_documents อีกครั้ง)
```

---

## สิ่งที่สร้าง / แก้ไข

### Backend

#### `app/api/v1/routers/applications.py`

เพิ่ม imports: `User`, `AuditLog`, `NotificationService`, `datetime`, `timezone`

เพิ่ม endpoint:
```
POST /applications/{app_id}/resubmit
```

**Logic:**
1. ตรวจสอบว่า applicant เป็นเจ้าของ (403 ถ้าไม่ใช่)
2. ตรวจสอบว่า `status == 'pending_documents'` (400 ถ้าไม่ใช่)
3. `app.status = 'submitted'`, `app.updated_at = now()`
4. บันทึก `AuditLog` action=`RESUBMIT`, old=`pending_documents`, new=`submitted`
5. `db.commit()`
6. Query staff ทุกคน → notify แต่ละคน:
   - title: `"ส่งเอกสารเพิ่มแล้ว — {app.application_no}"`
   - message: `"ผู้กู้ {ชื่อ} ได้ส่งเอกสารเพิ่มเติมสำหรับคำขอ {เลขที่} แล้ว กรุณาตรวจสอบ"`
   - type: `info`, link: `/staff/applications/{app_id}`
7. Notification failure → `pass` (ไม่ block resubmit)

**Response:** `{ success: true, message: "ส่งเอกสารเพิ่มเติมเรียบร้อยแล้ว รอเจ้าหน้าที่ตรวจสอบ" }`

---

### Frontend

#### `src/services/application.service.ts`

เพิ่ม method:
```typescript
async resubmit(id: string): Promise<{ success: boolean; message: string }> {
  const response = await api.post(`/applications/${id}/resubmit`)
  return response.data
}
```

#### `src/services/attachment.service.ts`

ปรับ `Attachment` interface ให้รองรับ optional fields:
```typescript
interface Attachment {
  id: string
  file_type: string
  original_filename: string
  file_size_bytes: number | null
  mime_type?: string | null
  uploaded_at?: string
}
```

#### `src/pages/ApplicationDetailPage.vue` (redesign section)

**State เพิ่มใหม่:**
- `uploadedDocs: ref<Attachment[]>([])` — โหลดจาก API เมื่อ `status === pending_documents`
- `newFileType: ref('other')` — ประเภทเอกสารที่เลือก
- `newFile: ref<File|null>(null)` — ไฟล์ที่เลือก
- `uploading: ref(false)`, `resubmitting: ref(false)`
- `fileInputRef` — ref สำหรับ reset input หลัง upload

**Functions:**
- `loadAttachments()` — `attachmentService.list(appId)` → `uploadedDocs`
- `onFileChange(e)` — อ่านไฟล์จาก input
- `uploadFile()` — `attachmentService.upload()` → toast → reset input → `loadAttachments()`
- `doResubmit()` — `applicationService.resubmit()` → `app.status = 'submitted'` → toast

**Upload Panel (แสดงเฉพาะ `status === 'pending_documents'`):**

```
┌─────────────────────────────────────────────┐
│ ⚠ เจ้าหน้าที่ขอเอกสารเพิ่มเติม              │
│   "[หมายเหตุ staff]"                         │
│   กรุณาอัปโหลดเอกสารที่ระบุ...              │
│─────────────────────────────────────────────│
│ อัปโหลดเอกสาร                               │
│ [ประเภทเอกสาร ▼]  [เลือกไฟล์]              │
│ [อัปโหลด]                                   │
│─────────────────────────────────────────────│
│ เอกสารที่แนบไว้แล้ว (N ไฟล์)               │
│ 📄 ประเภท — ชื่อไฟล์ · ขนาด    [ดู]        │
│─────────────────────────────────────────────│
│ [ยืนยันส่งเอกสารเพิ่มเติม]                  │
│ (disabled ถ้ายังไม่มีไฟล์)                  │
└─────────────────────────────────────────────┘
```

**Constraints:**
- ปุ่ม "ยืนยัน" disabled ถ้า `uploadedDocs.length === 0`
- หลัง `doResubmit()` สำเร็จ: `app.status = 'submitted'` → panel หายไปทันที → status badge เปลี่ยนเป็น "รออนุมัติ"
- รองรับไฟล์: `.pdf`, `.jpg`, `.jpeg`, `.png` (ตาม accept attribute)

---

## Flow สมบูรณ์ทั้งระบบ (หลัง Sprint 22)

```
[Borrower] ยื่นคำขอ
    ↓ notify staff
[Staff] ตรวจสอบ → pending_documents + remarks
    ↓ notify borrower
[Borrower] เห็น banner + หมายเหตุ
    ↓ อัปโหลดเอกสารเพิ่ม (1+ ไฟล์)
    ↓ กด "ยืนยันส่งเอกสารเพิ่มเติม"
    ↓ notify staff
[Staff] ตรวจสอบรอบสอง → approved | rejected | pending_documents (ซ้ำ)
    ↓ notify borrower
[Borrower] เห็นผลลัพธ์สุดท้าย
```

---

## Design Decisions

### D-1: Upload ทีละไฟล์ (ไม่ใช่ multi-select)
เหตุผล: ระบุ `file_type` ต่อไฟล์ได้ชัดเจน — staff รู้ว่าไฟล์ไหนคืออะไร

### D-2: ปุ่ม "ยืนยัน" disabled ถ้าไม่มีไฟล์
Borrower ต้องอัปโหลดอย่างน้อย 1 ไฟล์ก่อน resubmit ป้องกัน resubmit เปล่า

### D-3: อัปโหลดใช้ endpoint เดิม `POST /attachments/applications/{id}`
ไม่ต้องสร้าง endpoint ใหม่ — ownership check ครอบคลุม LoanApplication อยู่แล้ว
`AttachmentService.upload_attachment()` แทนที่ไฟล์ประเภทเดิมอัตโนมัติ (dedup)

### D-4: `app.status` อัปเดต in-memory หลัง resubmit สำเร็จ
ไม่ต้อง reload หน้า — upload panel หายไปทันที สถานะ badge เปลี่ยนเป็น "รออนุมัติ"

---

## Tests

Regression: **22/22 passed** ✅ (64s, SQLite)

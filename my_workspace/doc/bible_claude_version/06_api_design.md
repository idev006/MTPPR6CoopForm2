# 06 — API Design

---

## 6.1 API Conventions

```
Base URL    : /api/v1
Format      : JSON (application/json)
Auth        : Bearer token (JWT) ใน Authorization header
Version     : URL path versioning (/v1/)
Error       : RFC 7807 Problem Details
Pagination  : cursor-based (applications list)
```

### Standard Error Response Format

```json
{
  "type": "https://coopform.local/errors/validation-error",
  "title": "ข้อมูลไม่ถูกต้อง",
  "status": 422,
  "detail": "กรุณาตรวจสอบข้อมูลที่กรอก",
  "errors": [
    {
      "field": "national_id",
      "message": "เลขบัตรประชาชนต้องมี 13 หลัก"
    }
  ]
}
```

### HTTP Status Codes

| Status | การใช้งาน |
|--------|---------|
| 200 OK | GET สำเร็จ, PUT/PATCH สำเร็จ |
| 201 Created | POST สำเร็จ (สร้าง resource ใหม่) |
| 204 No Content | DELETE สำเร็จ |
| 400 Bad Request | Request body ผิดรูปแบบ |
| 401 Unauthorized | ไม่มี/หมดอายุ token |
| 403 Forbidden | มี token แต่ไม่มีสิทธิ์ (role ผิด) |
| 404 Not Found | ไม่พบ resource |
| 409 Conflict | ข้อมูลซ้ำ (email, member_code) |
| 422 Unprocessable | Validation error (Pydantic) |
| 500 Internal Error | Server error |

---

## 6.2 Authentication Endpoints

```
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
```

### POST /api/v1/auth/login

**Request:**
```json
{
  "email": "somchai@example.com",
  "password": "secretpassword"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "somchai@example.com",
    "full_name": "ด.ต. สมชาย รักชาติ",
    "role": "borrower",
    "member_code": "123456"
  }
}
```
*Refresh token เก็บใน HttpOnly Cookie อัตโนมัติ*

---

## 6.3 Member Profile Endpoints

```
GET    /api/v1/members/me/profile          → ดูโปรไฟล์ตัวเอง
PUT    /api/v1/members/me/profile          → แก้ Type A fields (ที่อยู่, เบอร์)
GET    /api/v1/members                     → [staff] รายการสมาชิกทั้งหมด
GET    /api/v1/members/{id}/profile        → [staff] ดูโปรไฟล์สมาชิกรายคน
PUT    /api/v1/members/{id}/financial      → [staff] แก้ Type B fields (เงินเดือน, หุ้น)
```

### GET /api/v1/members/me/profile — Response

```json
{
  "id": "uuid",
  "member_code": "123456",
  "title": "ด.ต.",
  "first_name": "สมชาย",
  "last_name": "รักชาติ",
  "national_id": "1-5501-12345-67-8",
  "position": "ผบ.หมู่ (ป.)",
  "department": "ภ.จว.พิษณุโลก",
  "phone": "081-234-5678",
  "addr": {
    "house_no": "99/1",
    "moo": "5",
    "road": "มิตรภาพ",
    "tambon": "ในเมือง",
    "amphur": "เมือง",
    "province": "พิษณุโลก"
  },
  "salary": 40000.00,
  "shares_amount": 50000.00
}
```

---

## 6.4 Draft Endpoints

```
POST   /api/v1/drafts                      → สร้าง Draft ใหม่ (หรือ upsert)
GET    /api/v1/drafts/{form_type}          → ดึง Draft ที่ค้างไว้
PUT    /api/v1/drafts/{id}                 → Auto-save (partial update)
DELETE /api/v1/drafts/{id}                 → ลบ Draft
```

### PUT /api/v1/drafts/{id} — Auto-save Request

```json
{
  "current_step": 2,
  "form_data": {
    "step1": { "...": "..." },
    "step2": { "loan_amount": "500000", "..." : "..." }
  }
}
```

---

## 6.5 Loan Application Endpoints

```
POST   /api/v1/applications                → Submit คำขอ (จาก Draft สมบูรณ์)
GET    /api/v1/applications                → ประวัติคำขอของตัวเอง (borrower)
GET    /api/v1/applications/{id}           → รายละเอียดคำขอ
POST   /api/v1/applications/{id}/cancel   → ยกเลิกคำขอ (borrower, status=submitted เท่านั้น)

# Staff endpoints
GET    /api/v1/staff/applications          → รายการคำขอทั้งหมด + filter
PUT    /api/v1/staff/applications/{id}/review → Approve/Reject
```

### POST /api/v1/applications — Submit Request

```json
{
  "form_type": "ordinary",
  "form_version": "1.0",
  "form_data": {
    "step1": { "...complete step 1 data..." },
    "step2": { "...complete step 2 data..." },
    "guarantors": [
      {
        "fullname": "พ.ต.ต. วีระ สุขใจ",
        "member_code": "234567",
        "position": "สว.",
        "department": "สภ.เมืองพิษณุโลก",
        "sig_base64": "data:image/png;base64,..."
      }
    ],
    "signatures": {
      "borrower_sig_base64": "data:image/png;base64,..."
    }
  }
}
```

**Response 201:**
```json
{
  "application_id": "uuid",
  "application_no": "ORD-2568-00001",
  "status": "submitted",
  "pdf_url": "/api/v1/pdf/uuid/download",
  "submitted_at": "2025-04-26T10:30:00Z"
}
```

### GET /api/v1/applications — Borrower History

```json
{
  "items": [
    {
      "id": "uuid",
      "application_no": "ORD-2568-00001",
      "form_type": "ordinary",
      "status": "approved",
      "requested_amount": 500000,
      "submitted_at": "2025-04-26T10:30:00Z",
      "reviewed_at": "2025-04-27T09:00:00Z",
      "review_remarks": null,
      "has_pdf": true
    }
  ],
  "total": 3,
  "next_cursor": null
}
```

### PUT /api/v1/staff/applications/{id}/review

```json
{
  "action": "approve",
  "remarks": "ข้อมูลครบถ้วน อนุมัติตามที่ขอ"
}
```
หรือ
```json
{
  "action": "reject",
  "remarks": "เอกสารไม่ครบ กรุณาแนบสำเนาบัตรประชาชน"
}
```

---

## 6.6 PDF Endpoints

```
GET    /api/v1/pdf/{application_id}/download   → Download PDF
POST   /api/v1/pdf/preview                     → Generate preview (ไม่บันทึก)
```

### GET /api/v1/pdf/{id}/download
- ตรวจสอบ ownership: เฉพาะเจ้าของหรือ staff เท่านั้น
- Response: `FileResponse` (application/pdf) พร้อม Content-Disposition header
- ถ้าไม่มีสิทธิ์: 403 Forbidden

---

## 6.7 API Security Summary

| Endpoint Group | ต้อง Auth | Role Required |
|----------------|-----------|---------------|
| POST /auth/login | ❌ | - |
| GET /auth/me | ✅ | any |
| GET/PUT /members/me/* | ✅ | borrower, staff |
| GET /members (list) | ✅ | staff only |
| PUT /members/{id}/financial | ✅ | staff only |
| CRUD /drafts | ✅ | borrower only |
| POST/GET /applications | ✅ | borrower (own data) |
| GET /staff/applications | ✅ | staff only |
| PUT /staff/applications/*/review | ✅ | staff only |
| GET /pdf/*/download | ✅ | owner or staff |

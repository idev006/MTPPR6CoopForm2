# Sprint 13 — Phase 5 Completion

**วันที่:** 2026-04-28
**เป้าหมาย:** ปิด Phase 5 ให้ครบ — ApplicationDetailPage, self-cancel, member management (staff)

---

## Deliverables

### 1. ApplicationDetailPage.vue (borrower)
- แสดงรายละเอียดคำขอกู้: หมายเลข, สถานะ, จำนวนเงิน, วัตถุประสงค์, วันที่
- ปุ่ม Cancel (แสดงเฉพาะ status = "submitted")
- ปุ่ม Download PDF (ถ้ามี)
- Back ไป Dashboard

### 2. GET /applications/{id} (borrower)
- endpoint ใหม่ใน applications.py
- ownership check: applicant_id == current_user["id"]
- คืน ApplicationDetailResponse

### 3. POST /applications/{id}/cancel (borrower)
- เปลี่ยน status: submitted → cancelled
- block ถ้า status ไม่ใช่ "submitted" (เช่น under_review, approved)
- บันทึก audit log

### 4. GET /members (staff)
- คืนรายชื่อ users ทั้งหมดที่ role = "borrower"
- พร้อม profile ข้อมูลพื้นฐาน

### 5. PUT /members/{id}/financial (staff)
- staff อัปเดต salary, shares_amount, existing_debt ของสมาชิกคนใดก็ได้
- ใช้ MemberProfileStaffUpdate schema ที่มีอยู่แล้ว

### 6. DashboardPage.vue — ประวัติคำขอ
- เปิด card "ประวัติคำขอ" ให้ navigate ไป application list
- แสดงรายการคำขอในหน้า Dashboard (inline list)

---

## Files Changed

### Backend
- `app/schemas/application.py` — เพิ่ม ApplicationDetailResponse
- `app/api/v1/routers/applications.py` — GET /{id}, POST /{id}/cancel
- `app/api/v1/routers/members.py` — GET /, PUT /{id}/financial

### Frontend
- `src/services/application.service.ts` — getById, cancel
- `src/pages/ApplicationDetailPage.vue` — full implementation
- `src/pages/DashboardPage.vue` — enable history + application list
- `src/services/member.service.ts` — staff methods (getAll, updateFinancial)

---

## Definition of Done
- [ ] borrower คลิก application ใน Dashboard แล้วเห็น detail page
- [ ] ปุ่ม Cancel ปรากฏเมื่อ status = "submitted", หายไปเมื่อ status อื่น
- [ ] staff เรียก GET /members ได้ครบ
- [ ] staff อัปเดต financial ผ่าน PUT /members/{id}/financial ได้

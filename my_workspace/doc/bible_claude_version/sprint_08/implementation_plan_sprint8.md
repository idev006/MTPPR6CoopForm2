# Implementation Plan — Sprint 8: Staff Workflow & Application Review

---

## 🎯 Goal
สร้างระบบหลังบ้านสำหรับเจ้าหน้าที่ (Staff) เพื่อตรวจสอบเอกสาร สั่งพิมพ์ PDF และดำเนินการอนุมัติ/ปฏิเสธคำขอกู้เงิน โดยยึดหลักความโปร่งใส (Auditability) และความถูกต้องทางกฎหมาย (Legal Snapshot)

---

## 🏛️ Architecture Alignment (6 เสาหลัก)
- **Layered:** แยก `StaffService` สำหรับงานตรวจสอบโดยเฉพาะ
- **Protocol:** ใช้ `ApplicationReviewSchema` ควบคุมการเปลี่ยนสถานะ
- **Auditability:** บันทึกทุกก้าวของเจ้าหน้าที่ลงใน `audit_logs`

---

## 🛠️ Proposed Changes

### 1. Backend Layer

#### [NEW] [staff_application.py](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/backend/app/api/v1/routers/staff_application.py)
- `GET /staff/applications`: รายการคำขอกู้สำหรับเจ้าหน้าที่
- `GET /staff/applications/{id}`: รายละเอียดเชิงลึก (รวม Parties Snapshot)
- `POST /staff/applications/{id}/status`: เปลี่ยนสถานะ (Reviewing / Approved / Rejected)
- `GET /staff/applications/{id}/pdf`: ดาวน์โหลด PDF ที่ Generated แล้ว

#### [NEW] [review_service.py](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/backend/app/services/review_service.py)
- Logic การเปลี่ยนสถานะ (State Transition)
- การบันทึกเหตุผล (Remarks) และการ snapshot เจ้าหน้าที่ผู้ตรวจ

#### [MODIFY] [audit_log.py](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/backend/app/models/audit_log.py)
- ตรวจสอบความพร้อมของตารางสำหรับการบันทึกร่องรอย

---

### 2. Frontend Layer

#### [NEW] Staff Dashboard (`/staff`)
- ระบบ Dashboard สำหรับเจ้าหน้าที่
- ตารางแสดงรายการคำขอกู้ พร้อมสถานะและสีสันที่ดูง่าย (DaisyUI)

#### [NEW] Application Review Detail
- หน้าจอแสดงข้อมูลที่ผู้กู้กรอกมา (ReadOnly)
- ส่วนการให้ความเห็น (Staff Remarks) และปุ่มกดอนุมัติ

---

## 🧪 Verification Plan
1. **End-to-End Workflow:** ผู้กู้ส่ง -> เจ้าหน้าที่เห็นใน List -> เจ้าหน้าที่กด Review -> สถานะเปลี่ยนเป็น Approved
2. **Audit Log Test:** ตรวจสอบใน DB ว่ามี Record บันทึกหรือไม่ว่าใครเป็นคนกดปุ่ม
3. **PDF Access:** ตรวจสอบว่าเจ้าหน้าที่สามารถเปิดดู PDF ที่ผู้กู้ส่งมาได้ถูกต้อง

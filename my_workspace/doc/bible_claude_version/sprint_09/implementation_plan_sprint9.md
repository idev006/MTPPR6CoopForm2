# Implementation Plan — Sprint 9: Supporting Documents & Production Readiness

---

## 🎯 Goal
ยกระดับคำขอกู้เงินให้สมบูรณ์ด้วยการเพิ่มระบบแนบไฟล์เอกสารประกอบ (Supporting Documents) และการเตรียมโครงสร้างพื้นฐานเพื่อรองรับการใช้งานจริง (Production)

---

## 🏛️ Architecture Alignment (6 เสาหลัก)
- **Layered:** เพิ่ม `AttachmentService` สำหรับงาน File I/O โดยเฉพาะ
- **Protocol:** ใช้ `AttachmentResponse` schema สำหรับการสื่อสารสถานะการอัปโหลด
- **Legal Snapshot:** ไฟล์แนบจะถูกเก็บถาวรและเชื่อมโยงกับ `application_id` เพื่อใช้เป็นหลักฐานทางกฎหมาย

---

## 🛠️ Proposed Changes

### 1. Backend Layer

#### [NEW] [attachment_service.py](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/backend/app/services/attachment_service.py)
- จัดการการอัปโหลดไฟล์ (Save to Disk + Record to DB)
- การตรวจสอบประเภทไฟล์ (MIME Type validation: JPG, PNG, PDF)
- การตั้งชื่อไฟล์แบบ Secure (UUID-based filenames)

#### [NEW] [attachments.py](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/backend/app/api/v1/routers/attachments.py)
- `POST /applications/{id}/upload`: รับไฟล์เอกสาร
- `GET /applications/{id}/list`: รายการไฟล์แนบของคำขอนั้นๆ
- `DELETE /attachments/{id}`: ลบไฟล์แนบ (เฉพาะสถานะ draft)

---

### 2. Frontend Layer

#### [NEW] `Step6Attachments.vue`
- หน้าจออัปโหลดไฟล์ใน Form Wizard
- รองรับการเลือกประเภทเอกสาร (บัตรประชาชน, ทะเบียนบ้าน, อื่นๆ)
- ระบบ Preview รูปภาพก่อน/หลังอัปโหลด

#### [MODIFY] `FormWizard.vue`
- เพิ่ม Step 6 เข้าไปในลำดับการกรอก

---

### 3. Infrastructure & DevOps

#### [MODIFY] `docker-compose.yml`
- เพิ่ม Volumes สำหรับ `/data/attachments` เพื่อให้ข้อมูลไม่หายเมื่อ Restart container
- ปรับค่า `UPLOAD_LIMIT` ใน config

---

## 🧪 Verification Plan
1. **Upload Test:** ทดลองอัปโหลดไฟล์ขนาดต่างๆ (ไม่เกิน 5MB) และตรวจสอบว่าไฟล์ไปอยู่ใน Folder ที่ถูกต้องหรือไม่
2. **Security Test:** ทดลองให้ User A เข้าถึงไฟล์แนบของ User B (ต้องถูก Block)
3. **End-to-End:** กรอกแบบฟอร์ม -> แนบไฟล์ -> เซ็นชื่อ -> กดส่ง -> เจ้าหน้าที่เห็นไฟล์แนบทั้งหมด

# 01 — Vision, Goals & Problem Statement

---

## 1.1 Problem Statement (ปัญหาที่ต้องแก้)

สหกรณ์ออมทรัพย์ในปัจจุบันใช้แบบฟอร์มกระดาษสำหรับการขอกู้เงิน ซึ่งมีปัญหาดังนี้:

```
ปัญหา 1: ความซับซ้อนของแบบฟอร์ม
  - แบบฟอร์ม "สัญญาเงินกู้สามัญ สอ.ภ.6" มี 15 หน้า, 150 fields
  - สมาชิกกรอกผิดพลาดบ่อย (ตัวสะกด, ตัวเลข, ลืมกรอก)
  - ต้องส่งคืนให้แก้ไขซ้ำหลายรอบ

ปัญหา 2: ขาด Validation ณ จุดกรอก
  - ไม่มีระบบตรวจสอบข้อมูลทันที
  - เจ้าหน้าที่ต้องตรวจสอบด้วยตามือทุกฉบับ

ปัญหา 3: ไม่มีระบบติดตามสถานะ
  - สมาชิกไม่รู้ว่าคำขอของตัวเองอยู่ขั้นตอนไหน
  - ไม่มีประวัติการยื่นคำขอ

ปัญหา 4: เอกสารกระดาษ
  - สูญหาย, เสียหายได้ง่าย
  - ค้นหาย้อนหลังยาก
  - ไม่มี Audit Trail
```

---

## 1.2 Vision Statement

> **"สมาชิกสหกรณ์สามารถยื่นคำขอกู้เงินได้ถูกต้องครบถ้วนตั้งแต่ครั้งแรก  
> ผ่านระบบออนไลน์ที่นำทางขั้นตอน ตรวจสอบข้อมูล และสร้าง PDF สมบูรณ์อัตโนมัติ"**

---

## 1.3 Project Goals (เป้าหมายโครงการ)

### Goal 1: ลดข้อผิดพลาดในการกรอกแบบฟอร์ม
- Validate ข้อมูลทุก field ก่อน submit
- แสดง error message ภาษาไทยที่เข้าใจง่าย
- Pre-fill ข้อมูลที่ระบบรู้อยู่แล้ว (ชื่อ, สังกัด, รหัสสมาชิก)

### Goal 2: สร้าง PDF คุณภาพสูงอัตโนมัติ
- PDF ที่ได้ต้องพร้อมส่งโดยไม่ต้องแก้ไขเพิ่มเติม
- รองรับลายเซ็นดิจิทัล (Signature Pad)
- Font ภาษาไทยถูกต้อง (TH Sarabun New)

### Goal 3: ระบบติดตามสถานะคำขอ
- สมาชิกเห็นสถานะ real-time
- เจ้าหน้าที่มี dashboard สำหรับ review
- ประวัติการยื่นคำขอย้อนหลังได้

### Goal 4: ระบบที่ Maintainable และ Extensible
- เพิ่มแบบฟอร์มประเภทใหม่ได้โดยไม่ต้อง refactor หลัก
- deploy และ backup ง่าย (Docker)

---

## 1.4 Project Objectives (วัตถุประสงค์เฉพาะ)

| # | Objective | KPI | Timeline |
|---|-----------|-----|----------|
| 1 | ระบบ Auth (login/logout) ทำงานได้ | Login สำเร็จ < 2 วินาที | Phase 2 |
| 2 | Multi-step Form กรอกข้อมูลได้ครบ 150 fields | Error rate < 5% | Phase 3 |
| 3 | PDF generate ได้ถูกต้อง | ตรงกับ PDF ต้นแบบ 100% | Phase 4 |
| 4 | Staff review workflow ทำงานได้ | Approve/Reject ได้ | Phase 5 |
| 5 | ระบบ deploy บน Docker ได้ | `docker-compose up` แล้วใช้งานได้ | Phase 6 |

---

## 1.5 Scope (ขอบเขต)

### In Scope (ทำในโปรเจกต์นี้)
- ระบบ Authentication (JWT)
- Multi-step Form Wizard สำหรับขอกู้เงิน
- PDF Generation (AcroForm fill + Signature overlay)
- Draft Auto-save
- Staff Review Dashboard
- ประวัติคำขอของสมาชิก
- รองรับหลายประเภทแบบฟอร์ม (โครงสร้างรองรับ แต่เริ่มด้วยกู้สามัญก่อน)
- File Attachment (โครงสร้างรองรับ ทำใน Phase ถัดไป)

### Out of Scope (ไม่ทำในโปรเจกต์นี้ตอนนี้)
- การชำระเงิน / โอนเงิน
- ระบบบัญชีสหกรณ์
- Mobile App (รองรับผ่าน Responsive Web แทน)
- Notification (LINE / Email) — เพิ่มได้ในอนาคต
- Digital Signature ที่มีผลทางกฎหมาย (ใช้ Signature Pad แบบ Canvas แทน)

---

## 1.6 Assumptions (สมมุติฐาน)

1. PDF ต้นแบบ (`สัญญาเงินกู้สามัญ สอ.ภ.6-fillable.pdf`) สร้างด้วย Adobe Acrobat Pro DC และมี AcroForm Named Fields พร้อมใช้
2. สมาชิกทุกคนมี email สำหรับ login
3. มี Server สำหรับ deploy (On-Premise หรือ VPS) — รองรับ Docker
4. ผู้ใช้งานไม่เกิน 200 คน, peak load ไม่เกิน 30 req/hr
5. ผู้ค้ำประกันนั่งอยู่ใกล้กับผู้กู้ขณะเซ็นชื่อ (Signature Pad ในหน้าจอเดียวกัน)

---

## 1.7 Constraints (ข้อจำกัด)

| ข้อจำกัด | รายละเอียด |
|---------|-----------|
| **PDF Format** | ต้องใช้ AcroForm fillable PDF เท่านั้น — coordinate-based approach ไม่รองรับ |
| **Font** | ต้องใช้ TH Sarabun New เท่านั้น (ข้อกำหนดของ PDF ต้นแบบ) |
| **PDF Library** | ใช้ pikepdf + reportlab เท่านั้น (pypdf.update_page_form_field_values พิสูจน์แล้วว่าไม่ทำงานกับ PDF นี้) |
| **Infrastructure** | Docker เท่านั้น — ไม่ใช้ Kubernetes, ไม่ใช้ Cloud-native services |
| **Budget** | ไม่มีค่าใช้จ่าย Third-party service (ใช้ Open Source ทั้งหมด) |

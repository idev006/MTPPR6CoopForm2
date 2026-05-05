# 02 — Requirements

---

## 2.1 Functional Requirements

### FR-AUTH: Authentication & Authorization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AUTH-01 | สมาชิกสามารถ Login ด้วย email + password ได้ | Must Have |
| FR-AUTH-02 | ระบบออก JWT Access Token (15 นาที) + Refresh Token (7 วัน) | Must Have |
| FR-AUTH-03 | Refresh Token เก็บใน HttpOnly Cookie | Must Have |
| FR-AUTH-04 | สมาชิกสามารถ Logout ได้ (invalidate token) | Must Have |
| FR-AUTH-05 | Route ที่ต้อง login จะ redirect ไปหน้า login อัตโนมัติ | Must Have |
| FR-AUTH-06 | Admin สร้าง account สมาชิก (สมาชิกไม่ register เอง) | Must Have |

### FR-PROFILE: Member Profile

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PRF-01 | สมาชิกดูข้อมูลส่วนตัวของตัวเองได้ | Must Have |
| FR-PRF-02 | สมาชิกแก้ไขข้อมูลส่วนตัว (ชื่อ, ที่อยู่, เบอร์โทร) ได้ | Must Have |
| FR-PRF-03 | ระบบ pre-fill ข้อมูลในแบบฟอร์มจาก Member Profile อัตโนมัติ | Must Have |
| FR-PRF-04 | Staff แก้ไขข้อมูลการเงินสมาชิก (เงินเดือน, ทุนหุ้น) ได้ | Must Have |
| FR-PRF-05 | Staff ดูข้อมูลสมาชิกทุกคนได้ | Must Have |

### FR-FORM: Form Wizard

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-FRM-01 | สมาชิกกรอกแบบฟอร์มขอกู้เงินสามัญผ่าน Multi-step Wizard | Must Have |
| FR-FRM-02 | แต่ละ Step มี Validation ก่อนไปขั้นต่อไป | Must Have |
| FR-FRM-03 | ระบบ Auto-save Draft ทุก 30 วินาที | Must Have |
| FR-FRM-04 | สมาชิกกลับมากรอกต่อจาก Draft ที่ค้างไว้ได้ | Must Have |
| FR-FRM-05 | สมาชิกย้อนกลับไป Step ก่อนหน้าได้ | Must Have |
| FR-FRM-06 | ผู้ค้ำประกันเซ็นชื่อด้วย Signature Pad Canvas | Must Have |
| FR-FRM-07 | ผู้กู้เซ็นชื่อด้วย Signature Pad Canvas | Must Have |
| FR-FRM-08 | สมาชิก Preview แบบฟอร์มก่อน Submit | Should Have |
| FR-FRM-09 | ค้นหาข้อมูลผู้ค้ำประกันด้วยรหัสสมาชิก | Should Have |
| FR-FRM-10 | ระบบรองรับแบบฟอร์มหลายประเภท (เพิ่มได้ในอนาคต) | Must Have (โครงสร้าง) |

### FR-PDF: PDF Generation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PDF-01 | ระบบ Generate PDF จากข้อมูลที่กรอกโดยอัตโนมัติเมื่อ Submit | Must Have |
| FR-PDF-02 | PDF ที่ได้ต้องแสดง Font ภาษาไทย (TH Sarabun New) ถูกต้อง | Must Have |
| FR-PDF-03 | PDF ที่ได้ต้องมีลายเซ็นจาก Signature Pad overlay ใน field ที่ถูกต้อง | Must Have |
| FR-PDF-04 | PDF ที่ได้ต้อง Lock ไม่ให้แก้ไข (ReadOnly fields) | Must Have |
| FR-PDF-05 | สมาชิกดาวน์โหลด PDF ของตัวเองได้ | Must Have |
| FR-PDF-06 | ระบบเก็บ metadata ของ PDF ที่ generate (ชื่อไฟล์, checksum, วันที่) | Must Have |
| FR-PDF-07 | Staff ดาวน์โหลด PDF ของสมาชิกได้ | Must Have |

### FR-APP: Loan Application Workflow

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-APP-01 | สมาชิก Submit คำขอกู้ได้ | Must Have |
| FR-APP-02 | สมาชิกดูสถานะคำขอของตัวเองได้ | Must Have |
| FR-APP-03 | สมาชิกดูประวัติคำขอย้อนหลังได้ | Must Have |
| FR-APP-04 | สมาชิกยกเลิกคำขอที่ยังไม่ได้รับการพิจารณาได้ | Should Have |
| FR-APP-05 | Staff ดูรายการคำขอทั้งหมดได้ (filter/search) | Must Have |
| FR-APP-06 | Staff อนุมัติ (Approve) คำขอได้พร้อม remark | Must Have |
| FR-APP-07 | Staff ปฏิเสธ (Reject) คำขอได้พร้อม remark | Must Have |
| FR-APP-08 | สมาชิกรับทราบผล Approve/Reject | Must Have |

### FR-FILE: File Attachment (Future)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-FILE-01 | สมาชิก Upload ไฟล์แนบ (สำเนาบัตร, slip) ได้ | Should Have (Phase ถัดไป) |
| FR-FILE-02 | ระบบ validate ประเภทไฟล์ (PDF, JPG, PNG) | Should Have |
| FR-FILE-03 | จำกัดขนาดไฟล์ต่อไฟล์ไม่เกิน 5 MB | Should Have |

---

## 2.2 Non-Functional Requirements

### Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-PERF-01 | Response time สำหรับ API ทั่วไป | < 500 ms (P95) |
| NFR-PERF-02 | PDF Generation time | < 5 วินาที |
| NFR-PERF-03 | Page load time (initial) | < 3 วินาที |
| NFR-PERF-04 | Concurrent users | รองรับ 50 concurrent โดยไม่ error |

### Security

| ID | Requirement |
|----|-------------|
| NFR-SEC-01 | Password เก็บแบบ hashed (bcrypt, cost factor ≥ 12) |
| NFR-SEC-02 | JWT Secret ต้องยาวอย่างน้อย 32 chars, เก็บใน .env |
| NFR-SEC-03 | CORS whitelist เฉพาะ Origin ของ frontend |
| NFR-SEC-04 | ไฟล์ PDF ดาวน์โหลดได้เฉพาะเจ้าของ + staff เท่านั้น |
| NFR-SEC-05 | Input validation ทั้ง Backend (Pydantic) และ Frontend (Zod) |
| NFR-SEC-06 | Rate limiting: max 60 req/min per IP |
| NFR-SEC-07 | HTTPS บน production (SSL termination ที่ Nginx) |

### Reliability

| ID | Requirement |
|----|-------------|
| NFR-REL-01 | Draft Auto-save ต้องไม่สูญหายเมื่อ browser refresh |
| NFR-REL-02 | PDF ที่ generate ต้องมี checksum ตรวจสอบความสมบูรณ์ |
| NFR-REL-03 | Database backup ได้ด้วย `pg_dump` |

### Usability

| ID | Requirement |
|----|-------------|
| NFR-USE-01 | UI ภาษาไทยทั้งหมด |
| NFR-USE-02 | Responsive — ใช้งานได้บน Desktop และ Tablet |
| NFR-USE-03 | Error message ภาษาไทย เข้าใจง่าย ไม่ใช่ technical error |
| NFR-USE-04 | Form Wizard แสดง progress indicator (Step 1/5 ฯลฯ) |

### Maintainability

| ID | Requirement |
|----|-------------|
| NFR-MNT-01 | เพิ่มแบบฟอร์มประเภทใหม่ได้โดยไม่แก้ Core logic |
| NFR-MNT-02 | Log ทุก API request (method, path, status, duration) |
| NFR-MNT-03 | Log rotation อัตโนมัติ (10 MB, เก็บ 30 วัน) |
| NFR-MNT-04 | Code ต้องผ่าน linting (ruff สำหรับ Python, ESLint สำหรับ TypeScript) |

---

## 2.3 Business Rules

| ID | Rule |
|----|------|
| BR-01 | สมาชิก 1 คน มี Draft ได้ไม่เกิน 1 ต่อ 1 ประเภทแบบฟอร์ม |
| BR-02 | Draft หมดอายุหลัง 30 วัน |
| BR-03 | คำขอที่ Submit แล้ว แก้ไขไม่ได้ (ต้องยกเลิกแล้วยื่นใหม่) |
| BR-04 | PDF จะ generate เมื่อ Submit เท่านั้น (ไม่ generate จาก Draft) |
| BR-05 | ผู้ค้ำประกันต้องมีอย่างน้อย 1 คน (max 3 คน ต่อคำขอ) — เปลี่ยนจาก 2 เป็น 3 ใน Sprint 6 เพื่อรองรับกรณีที่ PDF ต้องการลายเซ็นมากกว่า 2 คู่ |
| BR-06 | สมาชิกดู/โหลด PDF ได้เฉพาะของตัวเองเท่านั้น |
| BR-07 | Staff ดูและ review ได้ทุกคำขอ |
| BR-08 | คำขอที่ถูก Reject สมาชิกยื่นใหม่ได้ |

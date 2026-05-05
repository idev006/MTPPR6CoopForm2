# 17 — Sprint 7: PDF Engine & Submission Workflow

---

## 17.1 Overview

Sprint 7 focuses on the transition from a pure web-based data entry tool to a **Legally Binding Document Generator**. We implemented a World-Class PDF Engine and a robust submission workflow that snapshots data for legal integrity.

---

## 17.2 Key Features Implemented

### 1. High-Performance PDF Engine (`PdfEngine`)
- **Library:** `pikepdf` + `reportlab` (Fast & Precise).
- **Thai Font Rendering:** Full support for **TH Sarabun New** via custom Appearance Streams (/AP).
- **Signature Embedding:** Direct processing of Base64 signatures from the frontend into PDF XObjects.
- **Form Flattening:** Automatic setting of `/Ff` (ReadOnly) and `/F` (Hidden) flags for a clean, locked document.

### 2. Intelligent Field Mapping (`PdfService`)
- **One-to-Many Mapping:** Supported mapping a single web field (e.g., Borrower Name) to multiple PDF field IDs across 15 pages.
- **Data Transformation:** Automatic Thai date conversion (Buddhist Year) and currency formatting.
- **Extensibility:** Built with a pattern that allows adding new loan types (e.g., Emergency Loan) with minimal code changes.

### 3. Legal Snapshot Architecture
- **Refactored Database:** Moved from generic JSONB to a structured **Parties & Signatures** model.
- **Snapshot Pattern:** Data is copied into `application_parties` at the moment of submission, ensuring the contract remains valid even if the member updates their profile later.
- **Audit Trail:** Signatures are stored with timestamps, IP addresses, and metadata.

### 4. Advanced Frontend Validation
- **Zod Integration:** Implemented `ordinaryLoanSchema` for strict type checking.
- **Thai Error Messages:** User-friendly feedback for missing fields or invalid ID Card numbers.
- **Submission Feedback:** Integrated loading spinners, error alerts, and a success modal with Application Number display.

---

## 17.3 Technical Components

### Backend
- `app/engines/pdf_engine.py`: Low-level PDF manipulation.
- `app/services/pdf_service.py`: High-level field mapping.
- `app/services/application_service.py`: Orchestrates the submission lifecycle.
- `app/models/application_party.py` & `app/models/signature.py`: New database entities.

### Frontend
- `src/schemas/validation.ts`: Zod validation rules.
- `src/services/application.service.ts`: API bridge.
- `src/stores/form.store.ts`: State management for submission.

---

## 17.4 Verification Results
- [x] **PDF Integrity:** Generated PDF opens correctly in Acrobat/Chrome with Thai text visible.
- [x] **One-to-Many:** Name and Loan Amount appear correctly on Page 2, 4, and 5.
- [x] **Signatures:** Base64 signatures are sharp and correctly positioned.
- [x] **Workflow:** Draft session is cleared, and Application record is created successfully.

---

## 17.5 Next Steps (Sprint 8)
- **Staff Review Dashboard:** Allow staff to view submitted applications and download PDFs.
- **Email Notifications:** Notify staff when a new application is submitted.
- **Application History:** Allow borrowers to see their past submissions.

---

## 📝 17.6 Sprint Retrospective

### 🎓 Lessons Learned
- การใช้ `pikepdf` ร่วมกับ `reportlab` คือคู่หูที่ทรงพลังที่สุดในการทำ PDF Form Filling ใน Python เพราะให้ความยืดหยุ่นสูงในการวาด Font ไทยและจัดตำแหน่งลายเซ็น
- ลำดับชั้นของ PDF Fields (dot notation) มีความซับซ้อนกว่าที่คิด ต้องมีการเขียนฟังก์ชัน recursive เพื่อแกะฟิลด์ออกมาทั้งหมด

### 💡 Technics
- **Threadpool Integration:** การใช้ `run_in_threadpool` เพื่อแยกงานหนัก (PDF) ออกจาก Event Loop ของ FastAPI
- **One-to-Many Mapper:** การสร้างฟังก์ชัน `set_val` ที่รับทั้ง `str` และ `list` ช่วยลดความซ้ำซ้อนของโค้ดในการกรอกข้อมูลเดียวกันหลายที่

### ❌ ข้อผิดพลาด
- **Async/Sync Mismatch:** ในช่วงแรกมีการเขียน `ApplicationService` เป็นแบบ Sync ทำให้ขัดแย้งกับส่วนอื่นๆ ของระบบที่เป็น Async ทั้งหมด (ได้รับการแก้ไขแล้ว)

### ⚠️ ข้อควรระวัง
- **Base64 Payload:** ลายเซ็นต์แบบ Base64 มีขนาดใหญ่ หากในอนาคตมีผู้เกี่ยวข้องหลายคน ควรระวังเรื่องขนาดของ JSON Payload
- **Font Path:** ต้องระบุ Path ของ Font ให้แม่นยำ (Absolute Path) เมื่อรันในสภาพแวดล้อมที่ต่างกัน (Dev vs Docker)

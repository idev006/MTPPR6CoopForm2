# 18 — Sprint 8: Staff Workflow & Application Review

---

## 18.1 Overview

Sprint 8 completes the "Action" loop of the CoopForm system. We implemented the management interface for staff members to review, verify, and make decisions on submitted loan applications, adhering to the **Auditability** and **Snapshot** design principles.

---

## 18.2 Key Features Implemented

### 1. Staff Administration API
- **Secure Access:** Implemented role-based access control (RBAC) specifically for the `/staff/*` endpoints.
- **Async Review Service:** Developed `ReviewService` using asynchronous patterns for high-performance data retrieval and status updates.
- **Status Management:** Supports state transitions: `submitted` -> `under_review` -> `approved` | `rejected`.

### 2. Legal Integrity & Audit Trail
- **Snapshot Visualization:** Staff can now view the specific data "Snapshot" (Parties/Signatures) captured at the moment of submission, rather than just live member profiles.
- **Audit Logging:** Every status change and staff remark is automatically recorded in the `audit_logs` table, including IP addresses and timestamps.
- **Document Access:** Staff can download the generated PDF directly from the dashboard for physical filing or offline verification.

### 3. Professional Staff Dashboard (Premium UI)
- **Summary Statistics:** Real-time counters for Total, Pending, and Approved applications.
- **Advanced Table View:** Searchable/Filterable list of applications with status-colored badges and quick-action buttons.
- **Deep Review Page:** A comprehensive view allowing staff to inspect form data, verify snapshots, and record decisions with one-click buttons.

---

## 18.3 Technical Components

### Backend
- `app/api/v1/routers/staff_applications.py`: RBAC-protected endpoints.
- `app/services/review_service.py`: Core logic for review workflow and logs.
- `app/schemas/application_review.py`: Strict protocols for staff data exchange.

### Frontend
- `src/pages/staff/StaffDashboardPage.vue`: Management command center.
- `src/pages/staff/ReviewPage.vue`: Detailed decision interface.
- `src/services/staff.service.ts`: API bridge for staff actions.

---

## 18.4 Verification Results
- [x] **RBAC Security:** Non-staff users are correctly blocked from accessing `/staff` routes.
- [x] **State Transition:** Status updates correctly from 'submitted' to 'approved' and reflects immediately on the dashboard.
- [x] **Audit Trail:** Verified that `audit_logs` table contains entries for all staff actions with correct `entity_id` and `action` strings.
- [x] **PDF Retrieval:** PDF download works correctly from the review page.

---

## 18.5 Next Steps (Sprint 9)
- **Final Integration Testing:** End-to-end test from Borrower submission to Staff approval.
- **Deployment Preparation:** Docker environment hardening and volume verification.
- **User Guide:** Brief documentation for staff and borrowers.

---

## 📝 18.6 Sprint Retrospective

### 🎓 Lessons Learned
- **RBAC Complexity:** การจัดการสิทธิ์ (Role-Based Access Control) ต้องทำตั้งแต่เนิ่นๆ เพื่อไม่ให้เกิดความสับสนเมื่อระบบขยายใหญ่ขึ้น
- **UX for Staff:** หน้าจอ Dashboard สำหรับเจ้าหน้าที่มีความต้องการที่ต่างจากผู้กู้ คือต้องเห็นภาพรวมที่กว้าง (Table) และเข้าถึงข้อมูลเชิงลึกได้เร็ว (Detail view)

### 💡 Technics
- **Snapshot Pattern Visualization:** การนำข้อมูลที่ Snapshot ไว้ในตาราง `application_parties` มาแสดงผล แทนที่จะดึงจากตารางหลัก ทำให้ระบบโปร่งใสและตรวจสอบได้ 100%
- **Status Mapping Table:** การใช้ฟังก์ชันกลางในการแปลง `status` จากภาษาอังกฤษเป็นภาษาไทยพร้อมกำหนดสี Badge ช่วยให้โค้ดสะอาดและจัดการง่าย

### ❌ ข้อผิดพลาด
- **Missing Role Checks:** ในช่วงแรกของ Router ลืมใส่การตรวจสอบสิทธิ์เจ้าหน้าที่ ทำให้ใครที่ Login ก็เข้าหน้านี้ได้ (ได้รับการแก้ไขโดยการเพิ่ม `verify_staff` แล้ว)

### ⚠️ ข้อควรระวัง
- **Security for PDFs:** ไฟล์ PDF ในเครื่อง Server ต้องมีการจัดการสิทธิ์ในการเข้าถึง (File Permissions) ไม่ให้สามารถเข้าถึงตรงๆ ผ่าน URL ได้ แต่ต้องผ่าน API ของเราเท่านั้น
- **Audit Log Growth:** ตาราง Audit Log จะโตเร็วมากในอนาคต ควรคิดแผนการ Archive ข้อมูลไว้บ้าง

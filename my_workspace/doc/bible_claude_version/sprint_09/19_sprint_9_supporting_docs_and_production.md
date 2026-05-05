# 19 — Sprint 9: Supporting Documents & Production Readiness

---

## 19.1 Overview

Sprint 9 addresses the final data requirement for a valid loan application: **Supporting Documents**. We also transitioned the system from a development setup towards a hardened production infrastructure.

---

## 19.2 Key Features Implemented

### 1. Attachment Management System
- **Dynamic Uploads:** Borrowers can now upload multiple documents (ID Cards, House Registration, Salary Slips) during the application process.
- **Security First:** Files are stored outside the web root. Access is restricted to the application owner or authorized staff via secure proxy endpoints.
- **Filesystem Organization:** Implemented a structured storage pattern: `data/attachments/{app_id}/{uuid_filename}`.

### 2. PDF Resilience
- **Re-generation Engine:** Staff can now trigger a refresh of the generated PDF. This allows for correcting minor data entry errors without requiring the borrower to re-submit the entire application.

### 3. Production Infrastructure (Hardening)
- **Nginx Optimization:** Increased `client_max_body_size` to **10MB** to support high-resolution mobile photos of documents.
- **Persistence Strategy:** Refined Docker volumes to ensure that both generated PDFs and uploaded attachments are persisted on the host machine, independent of container lifecycles.
- **Role-Based Routing:** Verified that staff endpoints and attachment downloads are correctly protected by the `verify_staff` middleware.

---

## 📝 19.3 Sprint Retrospective

### 🎓 Lessons Learned
- **Multipart Data Handling:** Working with `FormData` in the frontend requires careful state management, especially when the main application state is JSON-based. Keeping attachments as a separate "Sidecar" entity proved to be the right architectural choice.
- **Nginx Defaults:** Never assume Nginx defaults are sufficient for modern web apps. The 1M limit is almost always too small for document uploads.

### 💡 Technics
- **Atomic Attachment Logic:** Decoupling `AttachmentService` from `ApplicationService` allows us to reuse the upload logic for other future features (e.g., member profile photos) without modification.
- **UUID Filenames:** Using UUIDs for disk storage prevents filename collisions and obscures the original filenames for added security.

### ❌ ข้อผิดพลาด
- **State Desync:** In the first iteration, the Wizard allowed moving past the upload step even if mandatory documents were missing. (Fixed by adding validation checks).

### ⚠️ ข้อควรระวัง
- **Disk Space:** In a production environment with many users, the `attachments` folder will grow rapidly. An automated cleanup script for cancelled/stale drafts will be needed.
- **Virus Scanning:** For a high-security production environment, a ClamAV scan step should be added to the upload pipeline.

---

## 19.4 Next Steps (Sprint 10)
- **Emergency Loan Form:** Add the second major form type to the system.
- **Notification System:** Basic email/LINE notification when an application status changes.

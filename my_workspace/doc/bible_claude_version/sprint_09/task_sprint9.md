# Sprint 9 Task List — Supporting Documents & Production Readiness

- [x] **[Backend] Attachment Logic**
    - [x] Create `app/services/attachment_service.py` (File I/O)
    - [x] Create `app/api/v1/routers/attachments.py` (Upload/Download endpoints)
    - [x] Register attachments router in `app/main.py`

- [x] **[Frontend] Document Upload UI**
    - [x] Create `components/wizard/Step6Attachments.vue` (Renamed to StepAttachments.vue)
    - [x] Update `FormWizard.vue` to include Step 6
    - [x] Implement File Preview and Upload progress in UI

- [x] **[Backend] PDF Re-generation Support**
    - [x] Add `regenerate_pdf` endpoint for staff in `staff_applications.py`

- [x] **[Infrastructure] Production Hardening**
    - [x] Update `docker-compose.yml` with persistent volumes for attachments
    - [x] Setup Nginx `client_max_body_size 10M`

- [x] **[Verification] E2E Walkthrough**
    - [x] Complete flow: Borrower (Submit + Attach) -> Staff (Review + Download Attachments)

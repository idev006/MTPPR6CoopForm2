# Sprint 8 Task List — Staff Workflow & Application Review

- [x] **[Backend] Setup Review Schemas**
    - [x] Create `app/schemas/application_review.py`
    - [x] Define `ReviewRequest` and `StaffApplicationDetail` protocols

- [x] **[Backend] Implementation of Review Service**
    - [x] Create `app/services/review_service.py`
    - [x] Implement `approve_application()` and `reject_application()`
    - [x] Add `audit_log` integration for every status change

- [x] **[Backend] API Endpoints for Staff**
    - [x] Create `app/api/v1/routers/staff_applications.py`
    - [x] Implement `GET /` (List for staff)
    - [x] Implement `POST /review` (Submit decision)
    - [x] Register router in `app/main.py`

- [x] **[Frontend] Staff Dashboard Foundation**
    - [x] Create `StaffDashboard.vue`
    - [x] Setup route `/staff` in `router/index.ts`
    - [x] Implement Application List table (DaisyUI)

- [x] **[Frontend] Application Review Detail View**
    - [x] Create `StaffApplicationReview.vue`
    - [x] Implement read-only form data display
    - [x] Add Approval/Rejection action buttons

- [x] **[Verification]**
    - [x] Test status transitions (submitted -> approved)
    - [x] Verify Audit Log records in DB

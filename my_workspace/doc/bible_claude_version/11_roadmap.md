# 11 — Development Roadmap

---

## 11.1 Phase Overview

```
Phase 1: Foundation & Infrastructure     (1-2 สัปดาห์)
Phase 2: Authentication & Member System  (1-2 สัปดาห์)
Phase 3: Core Form Engine                (2-3 สัปดาห์)
Phase 4: PDF Engine Integration          (1-2 สัปดาห์)
Phase 5: Workflow & Staff UI             (1-2 สัปดาห์)
Phase 6: Testing & Deployment            (1 สัปดาห์)
──────────────────────────────────────────────────────
รวมประมาณ: 7-12 สัปดาห์
```

---

## Phase 1 — Foundation & Infrastructure ✅ DONE (Sprint 3, 2026-04-26)

**เป้าหมาย:** project ขึ้นมาทำงานได้บน Docker พร้อม database

### Backend Tasks
- [x] สร้าง directory structure ตาม Section 10.2
- [x] FastAPI scaffold (`main.py`, health endpoint)
- [x] SQLAlchemy models ทุกตาราง (users, member_profiles, loan_applications, ...)
- [x] Alembic setup + migration `001_initial_schema` + `002_loan_tables`
- [x] `config.py` โหลด TOML + .env
- [x] `logging_setup.py` ด้วย loguru
- [x] Custom exception handlers (RFC 7807)

### Infrastructure Tasks
- [x] `docker-compose.yml` (nginx + api + db)
- [x] `docker-compose.prod.yml` (production configuration)
- [x] `nginx/conf.d/coopform.conf`
- [x] `.env.example`
- [x] Bind mounts ทดสอบ persistence
- [x] `config/logging.toml`, `config/security.toml`, `config/forms/loan_ordinary.toml`

### Frontend Tasks
- [x] Vite + Vue 3 + TypeScript scaffold
- [x] TailwindCSS v4 + DaisyUI v5 setup
- [x] `api.service.ts` (Axios instance + interceptors)
- [x] Pinia stores scaffold
- [x] Vue Router scaffold

**Definition of Done:** `GET /api/health` → 200 OK, DB 7 tables, alembic rev 002 ✅

---

## Phase 2 — Authentication & Member System ✅ DONE (Sprint 4, 2026-04-26)

**เป้าหมาย:** Login/Logout ทำงานได้, Profile ดูและแก้ไขได้

### Backend Tasks
- [x] `auth_service.py` (JWT create/verify, bcrypt โดยตรง — ไม่ใช้ passlib)
- [x] `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`
- [x] `GET /auth/me`
- [x] `dependencies.py` (get_current_user, require_role)
- [x] `member_service.py` (get_profile, update_type_a, update_type_b)
- [x] `GET/PUT /members/me/profile`
- [ ] `GET /members` (staff only)
- [ ] `PUT /members/{id}/financial` (staff only)

### Frontend Tasks
- [x] `LoginPage.vue` + `useAuth.ts` + `auth.service.ts`
- [x] Route guards (requiresAuth + role check)
- [x] `DashboardPage.vue` (skeleton)
- [x] `StaffDashboardPage.vue` (skeleton)
- [x] JWT auto-refresh interceptor ใน `api.service.ts`
- [x] `ProfilePage.vue` + แก้ไข Type A fields
- [x] `UiInput.vue` primitive (Sprint 5.5)

**Definition of Done:** Login → Dashboard ✅, Staff → /staff ✅, Auth endpoints ครบ ✅
> หมายเหตุ: member profile endpoints ยังไม่ทำ → ย้ายไปเริ่มต้น Phase 3

---

## Phase 3 — Core Form Engine ✅ DONE (Sprint 5/5.5/6, 2026-04-26)

**เป้าหมาย:** Multi-step Form กรอกได้ครบ + Auto-save + Signature

### Backend Tasks
- [x] `POST /drafts` (upsert)
- [x] `GET /drafts/{form_type}`
- [x] `PUT /drafts/{id}` (auto-save)
- [x] Pydantic schemas (member.py, draft.py)
- [x] `draft_service.py` + `member_service.py`
- [x] Zod validation สำหรับ OrdinaryLoanFormData (Sprint 6)

### Frontend Tasks
- [x] `OrdinaryLoanWizard.vue` — 7-tabs TABS registry + role filter (`src/forms/ordinary-loan/`)
- [x] `Step1PersonalInfo.vue` (Composition API, v-model) — `src/forms/shared/`
- [x] `Step2LoanDetails.vue` — `src/forms/ordinary-loan/`
- [x] `Step3Guarantors.vue` — `src/forms/ordinary-loan/`
- [x] `StepAttachments.vue` — `src/forms/shared/` ⚠️ known violation (ดู ADR-008)
- [x] `Step4SignatureHub.vue` — `src/forms/shared/`
- [x] `Step5StaffVerification.vue` — `src/forms/staff/`
- [x] `Step6ContractFinalization.vue` — `src/forms/staff/`
- [x] `BaseWizardLayout.vue` — `src/forms/shared/`
- [x] auto-save ใน `form.store.ts` (watch + setTimeout 30s)
- [x] `ProfilePage.vue`
- [x] `UiSignaturePad.vue` — signature_pad wrapper
- [x] 100% PDF Compliance Fields (ID Card, Addresses, Witness)
- [ ] Pre-fill Step1 จาก `profileStore.step1Prefill` → Sprint 11

**Definition of Done:** กรอกแบบฟอร์มได้ครบ 7 tabs, รองรับ Signature Hub (Tablet Walk), ข้อมูลครบถ้วนตาม PDF ✅

---

## Phase 4 — PDF Engine Integration ✅ DONE (Sprint 7, 2026-04-27)

**เป้าหมาย:** Submit → PDF ออกมา ถูกต้องและดาวน์โหลดได้

### Backend Tasks
- [x] `app/engines/pdf_engine.py` (core logic — ย้ายจาก Sprint 1/2 test.py)
- [x] `app/services/pdf_service.py` (field mapping + embed signature + save)
- [x] `app/services/application_service.py` (submit workflow + legal snapshot)
- [x] `POST /applications` (submit + trigger PDF gen)
- [x] `GET /pdf/{id}/download` (FileResponse + ownership check)
- [x] Application number generation (ORD-2568-XXXXX)
- [x] `app/models/application_party.py` + `app/models/signature.py` (Snapshot Pattern)
- [x] Alembic migration for application_parties + signatures + generated_pdfs

### Frontend Tasks
- [x] `src/schemas/validation.ts` (Zod ordinaryLoanSchema + emergencyLoanSchema)
- [x] `src/services/application.service.ts`
- [x] Submit flow ใน `form.store.ts` (`submitForm()`)
- [x] Success modal หลัง submit (แสดง application_no)
- [x] ปุ่ม Download PDF

**Definition of Done:** Submit → ได้ PDF ถูกต้อง 150 fields ครบ, Download ได้ ✅

---

## Phase 5 — Workflow & Staff UI ✅ DONE (Sprint 8/9, 2026-04-27)

**เป้าหมาย:** Staff review ได้, สมาชิกเห็นสถานะ

### Backend Tasks
- [x] `GET /staff/applications` (filter by status, date, search)
- [x] `PUT /staff/applications/{id}/review` (approve/reject)
- [x] `GET /applications` (borrower history)
- [x] **Sprint 9: Supporting Documents & Validation Architecture**
    - [x] Attachment System (Upload/Download PDF 10MB)
    - [x] `AttachmentService` (decoupled, UUID filenames, secure proxy)
    - [x] Validation Engine (Chain of Responsibility Pattern)
    - [x] The Cockpit (Central Control Dashboard)
    - [x] PDF Re-generation endpoint (staff trigger)
    - [x] Frontend/Backend Config Sync (SSOT)
- [x] `GET /applications/{id}` (detail)
- [x] `audit_logs` table + logging ทุก staff action (IP, timestamp, remark)
- [x] Alembic migration `audit_logs`
- [x] `POST /applications/{id}/cancel` (borrower self-cancel) — Sprint 13

### Frontend Tasks
- [x] `StaffDashboardPage.vue` (รายการคำขอทั้งหมด, filter, stats)
- [x] `ReviewPage.vue` (ดูรายละเอียด, approve/reject form, snapshot visualization)
- [x] `DashboardPage.vue` (borrower — ประวัติคำขอ + สถานะ)
- [x] `StepAttachments.vue` (upload wizard step) — ⚠️ known violation ดู ADR-008
- [x] `src/stores/toast.store.ts` (global toast system — Sprint 10)
- [x] `ApplicationDetailPage.vue` (standalone detail view) — Sprint 13
- [ ] `ApplicationStatusBadge.vue` (reusable badge component)

**Definition of Done:** Staff approve → สมาชิกเห็นสถานะ "อนุมัติ" ✅

---

## Phase 6 — Testing & Deployment 🟡 PARTIAL (Sprint 9, 2026-04-27)

**เป้าหมาย:** Production ready

### Testing Tasks
- [ ] `test_auth.py` (login, refresh, invalid credentials)
- [ ] `test_applications.py` (submit, status flow)
- [ ] `test_pdf_service.py` (fill_pdf output validation)
- [ ] Frontend: Vitest unit tests สำหรับ Zod schemas
- [ ] E2E: Manual UAT กับ stakeholders

### Deployment Tasks
- [x] `docker-compose.prod.yml` (production configuration)
- [x] Nginx `client_max_body_size` 10MB (Sprint 9)
- [x] Docker volumes persistence verified (pdf_generated + attachments)
- [x] Role-based routing verified (staff endpoints protected)
- [ ] SSL certificate setup (Nginx)
- [x] `backup.sh` script (รูปแบบ pg_dump + tar)
- [ ] Log rotation verification
- [x] Health check endpoints (`/api/health`)
- [ ] `README.md` — production deployment guide

---

## 11.2 Sprint Planning

```
Sprint 1  (done ✅) : PDF Engine research + pikepdf proof of concept
Sprint 2  (done ✅) : Fill all 150 fields, sign_ & rdo_ support
Sprint 3  (done ✅) : Phase 1 — Infrastructure + DB scaffold (2026-04-26)
Sprint 4  (done ✅) : Phase 2 — Auth endpoints + LoginPage + DashboardPage (2026-04-26)
Sprint 4.5 (done ✅): Dev env setup + DaisyUI v5 + Tailwind v4 migration (2026-04-26)
Sprint 5  (done ✅) : Phase 3 — Form Wizard (Tabs, Step 1-3) + member profile endpoints (2026-04-26)
Sprint 5.5 (done ✅): UI Architecture — Bai Jamjuree font, 32 DaisyUI themes, Pinia redesign (2026-04-26)
Sprint 6  (done ✅) : Phase 3 — 7-Tab Wizard + Signature Hub + 100% PDF Compliance (2026-04-26)
Sprint 7  (done ✅) : Phase 4 — PDF Mapping & Generation Engine (2026-04-27)
Sprint 8  (done ✅) : Phase 5 — Staff Workflow & Application Review (2026-04-27)
Sprint 9  (done ✅) : Phase 5/6 — Supporting Docs, Validation Engine, Cockpit, Production Hardening (2026-04-26/27)
Sprint 10 (done ✅) : Architecture Decoupling (src/forms/), Toast, Auto-draft fix, Notification bug fix (2026-04-28)
Sprint 11 (done ✅) : StepAttachments refactor, Emergency Loan E2E, Pre-fill Step1 fix (2026-04-28)
Sprint 12 (done ✅) : Code Audit (19 bugs found) + all Critical/High/Medium/Low fixes (2026-04-28)
                      C-01: current_user dict access across 3 routers
                      C-02: system.py endpoints unauthenticated
                      C-03: User.username → first_name/last_name in review_service
                      C-04: Session restore on page reload (App.vue refresh)
                      H-01+H-02: /applications/emergency endpoint + field key fixes
                      H-03: Zod schema sync with TypeScript types
                      H-04: GuarantorInfo.address → current_addr
                      H-05: None check in download endpoint
                      H-06: Hardcoded paths → settings.DATA_DIR
                      H-07: Notification query order (WHERE before LIMIT)
                      M-01: Notification mark_as_read ownership check
                      M-03: payout_method type union (added 'cheque')
                      M-05: stepEmergency added to reset()
                      L-01: Deleted useAutoSave.ts (dead code)
                      L-02: secure cookie tied to ENVIRONMENT
Sprint 13 (done ✅) : Phase 5 Completion — ApplicationDetailPage, self-cancel, member management (2026-04-28)
                      ApplicationDetailPage.vue — full detail view with timeline + cancel modal
                      GET /applications/{id} — borrower detail with ownership check
                      POST /applications/{id}/cancel — status guard (submitted only)
                      DashboardPage — inline application history table + clickable rows
                      GET /members (staff) — list all borrowers with financial fields
                      PUT /members/{id}/financial (staff) — update salary/shares/debt
                      MemberListItem schema added to member.py
Sprint 14 (done ✅) : กู้สามัญ PDF Complete — all 193 fields pages 1-5 (2026-04-28)
Sprint 15 (done ✅) : E2E Test — Dummy Data → Web Form → PDF (2026-04-29)
Sprint 16 (done ✅) : Automated Tests — 22 backend + 8 frontend = 30 tests (2026-04-29)
Sprint 27 (done ✅) : Migration Completeness + PostgreSQL Readiness (2026-05-03)
                      003_fix_attachment_fk: drop FK บน attachments.application_id (batch_alter_table recreate="always")
                      004_application_parties_signatures: สร้างตาราง application_parties + signatures (ขาดมาตั้งแต่ Sprint 7)
                      005_notifications: สร้างตาราง notifications (ขาดมาตั้งแต่ Sprint 21)
                      006_cancel_fields: เปลี่ยน down_revision จาก "002" → "005"
                      application_party.py + signature.py: refactor postgresql.UUID → sa.Uuid (Mapped[] style)
                      Cancel endpoint: body optional (Optional[CancelRequest] = Body(default=None))
                      alembic upgrade head บน fresh DB ได้ครบ 10 ตาราง ✅
                      pytest 22/22 passed ✅
                      doc: sprint_27/36_sprint_27_migration_completeness.md
Sprint 26 (done ✅) : Cancel Application Enhancement (2026-04-30)
                      migration 006_cancel_fields: เพิ่ม cancelled_at + cancel_reason ใน loan_applications
                      POST /applications/{id}/cancel รับ CancelRequest{reason?}, set cancelled_at, AuditLog CANCEL, notify staff
                      ApplicationDetailPage: Cancel Modal มี textarea เหตุผล (optional, max 500), แสดง cancel_reason + cancelled_at
                      DashboardPage: แยก active (submitted/under_review/pending_documents/approved) vs ปิดแล้ว (cancelled/rejected) — collapsible
                      navigation.ts: เพิ่ม "🚫 ยกเลิกแล้ว" → /staff?status=cancelled ใน Staff nav
                      doc: sprint_26/35_sprint_26_cancel_application.md
Sprint 25 (done ✅) : Navigation Menu System — Left Sidebar + Bottom Nav (2026-04-30)
                      navigation.ts: NavItem/NavGroup/NavEntry schema + StaffBadgeKey
                      useNavBadges.ts: poll 60s ดึง submitted/under_review/pending_documents count
                      NavItem.vue: active state (exact + query-aware) + badge
                      NavGroup.vue: DaisyUI details/summary collapsible group
                      AppSidebar.vue: DaisyUI drawer-side, menu menu-sm, sidebar 240px borrower/staff แยก role
                      MobileTopBar.vue: hamburger = label for app-drawer (DaisyUI CSS toggle)
                      BottomNav.vue: 4 จุดหลัก fixed bottom + badge count
                      AppLayout.vue: DaisyUI drawer lg:drawer-open layout
                      ThemePicker: prop dropdownClass (dropdown-top ใน sidebar, dropdown-end ใน topbar)
                      doc: sprint_25/34_sprint_25_navigation_menu.md
Sprint 24 (done ✅) : Draft Resume UX — Dashboard draft card (2026-04-30)
                      DashboardPage: draft section แสดง card + progress bar + "ดำเนินการต่อ" + "ลบร่าง"
                      loadDrafts(): Promise.allSettled โหลด loan_ordinary + loan_emergency พร้อมกัน
                      continueDraft(): navigate ตรง (wizard โหลด draft จาก server เอง)
                      discardDraft(): draftService.delete() + toast + ลบ card ทันที
Sprint 23 (done ✅) : Production Hardening (2026-04-30)
                      A: Rate limiting — slowapi @limiter.limit("5/minute") บน POST /auth/login
                      B: Magic bytes validation — MagicBytesValidator ตรวจ header จริง (PDF/JPG/PNG)
                      C: README.md — setup guide + flow + credentials + security notes
                      D: Error pages — NotFoundPage.vue (404) + ForbiddenPage.vue (403) + router guard → 403
                      run_backend.bat ชี้ system Python ที่มี FastAPI/uvicorn จริง
Sprint 22 (done ✅) : Complete pending_documents Flow (2026-04-30)
                      POST /applications/{id}/resubmit — status pending_documents → submitted + notify staff + AuditLog
                      ApplicationDetailPage: upload panel (ประเภทเอกสาร + file input + อัปโหลด)
                      แสดงรายการไฟล์ที่แนบแล้ว (list) + ปุ่ม "ดู" (blob URL)
                      ปุ่ม "ยืนยันส่งเอกสารเพิ่มเติม" (disabled ถ้าไม่มีไฟล์)
                      หลัง resubmit: app.status อัปเดต in-memory → panel หายทันที
                      applicationService.resubmit() + Attachment interface เพิ่ม optional fields
                      pytest 22/22 passed ✅
Sprint 21 (done ✅) : Staff Review Redesign + Bidirectional Communication (2026-04-30)
                      ReviewPage.vue — 2-column layout: structured form data (left) + docs/decision (right)
                      pending_documents status: staff ขอเอกสารเพิ่ม + borrower เห็น banner + timeline step
                      GET /staff/applications?status= filter + attachments[] ใน detail endpoint
                      staffService: openPdf/openAttachment blob URL (fix 401 on PDF)
                      StaffDashboardPage: filter tabs ทุกสถานะ (submitted/under_review/pending_docs/approved/rejected)
                      ApplicationDetailPage: pending_documents banner + รวม review_remarks ในทุกสถานะ
                      application_service: notify staff ทุกคนเมื่อ submit ใหม่ (link → /staff/applications/{id})
                      review_service: STATUS_CONFIG ครบ 4 สถานะ, message template มี context + remarks
                      NotificationBell: poll 30s(staff)/60s(borrower), type dot+badge, click-outside, memory leak fix
Sprint 20 (done ✅) : Confirm Submit Modal — checklist ก่อน submit (2026-04-30)
                      form.store.ts — pdfViewed flag + setPdfViewed()
                      StepReview.vue — setPdfViewed() เมื่อ openPdf() สำเร็จ
                      attachment.service.ts — openFile(id) blob viewer
                      OrdinaryLoanWizard.vue — confirm modal: PDF/ลายเซ็น/เอกสาร checklist
                      Block submit ถ้า: PDF ไม่ดู / ลายเซ็นขาด / required docs ขาด
                      required docs dynamic ตาม guarantors.length
Sprint 19 (done ✅) : Submit Application UX — success modal + draft cleanup (2026-04-29)
                      DELETE /drafts/{draft_id} endpoint (204) + delete_draft() service
                      draftService.delete() — frontend service method
                      form.store.ts submitForm() — ลบ draft หลัง submit สำเร็จ (silent fail)
                      OrdinaryApplicationPage.vue — success modal แสดงเลขคำขอ + ปุ่ม "ไปยังหน้าหลัก"
                      modal → form.reset() + redirect dashboard
Sprint 18 (done ✅) : Borrower Review + PDF Preview Step (2026-04-29)
                      StepReview.vue — สรุปข้อมูล + 4 states PDF preview (idle/generating/ready/error)
                      POST /applications/ordinary/preview — สร้าง temp PDF ใน data/previews/{user_id}.pdf
                      GET /applications/preview/download — FileResponse ส่งไฟล์ PDF (auth required)
                      preview.service.ts — frontend service layer
                      OrdinaryLoanWizard — เพิ่ม "ตรวจสอบข้อมูล" tab (borrower only, เป็น last tab ก่อน submit)
                      pytest 22/22 passed (no regression)
Sprint 17 (done ✅) : Form Engine Foundation — TOML-driven config, emergency loan pilot (2026-04-29)
                      config/forms/loan_emergency.toml — steps + pdf_fields (direct/computed/concat/signature)
                      backend/app/engines/form_engine.py — FormEngine class (TOML → PDF field mapping)
                      pdf_service.py — fill_via_engine() + ลบ _map_emergency_loan() (engine-driven แทน)
                      backend/app/api/v1/routers/forms.py — GET /forms/{form_id}/config endpoint
                      frontend/src/forms/registry.ts — COMPONENT_REGISTRY (string → Vue component)
                      frontend/src/composables/useFormConfig.ts + form.config.service.ts
                      frontend/src/forms/GenericFormWizard.vue — renders steps from TOML config
                      EmergencyLoanWizard.vue refactored → 7 lines (thin wrapper ของ GenericFormWizard)
                      form.store.ts — getStep()/setStep() generic accessor สำหรับ GenericFormWizard
                      pytest 22/22 passed (no regression)
                      pytest.ini + conftest.py: test_engine/db_session/client fixtures, fresh session per request
                      test_auth.py (5), test_applications.py (5), test_thai_baht.py (12)
                      vitest.config.ts + validation.test.ts (8 Zod cases)
                      Bug fix: selectinload(generated_pdf) in GET /applications/{id} (MissingGreenlet)
                      config.py: ASSETS_DIR added
                      assets/templates/loan_ordinary_v1.pdf copied from tee_temp
                      src/dev/dummyData.ts: full dummy data all steps + 6 signatures
                      BaseWizardLayout.vue: "🧪 เติมข้อมูลทดสอบ" button (DEV only)
                      UAT PASSED: 116/193 fields filled, 77 hidden (empty), PDF 4.9MB OK
                      Bug fixes: pdf_engine.py pikepdf 9.x resolve() guards, app.id → str(app.id)
                      types/form.ts — SignatureData + signer_name/signer_position, Step6Data + *_name fields
                      Step4SignatureHub.vue — superior name/position inputs before signing
                      Step6ContractFinalization.vue — manager/chairman/witness name inputs
                      app/core/config.py — INTEREST_RATE_ORDINARY = 5.75
                      app/utils/thai_baht.py — baht_to_text() (new utility, all cases tested)
                      app/services/pdf_service.py — complete _map_ordinary_loan() pages 1-5:
                        P1: checklist 18 items have/nohave checkboxes
                        P2: all register_addr fields, amount_text Thai words, shares_amount,
                            chk1 loan type, nguad_amount, payout method checkboxes, bank fields
                        P3: supervisor fullname/position, ch2/ch3 checkboxes
                        P4: full register_addr, amount_text, interest_rate from config,
                            monthly_payment calc, period_text, start_month, pay method checkboxes
                        P5: witness/chairman/manager names, recv_info amount_text+date,
                            spouse_agreement place/date, single borrower → dash fill
```

---

## 11.3 Tech Debt & Future Enhancements

| Item | Priority | Status |
|------|----------|--------|
| Supporting Docs (แนบไฟล์ บัตร ปชช./ทะเบียนบ้าน) | **High** | ✅ Done Sprint 9 |
| PDF Re-generation (เผื่อกรณีข้อมูลผิดหลังอนุมัติ) | Medium | ✅ Done Sprint 9 |
| Pre-fill Step1 จาก profileStore.step1Prefill | Medium | ✅ Done Sprint 11 |
| **[REFACTOR] StepAttachments → attachment.service.ts** | **High** | ✅ **Done Sprint 11** |
| เพิ่ม form type: กู้ฉุกเฉิน | Medium | ✅ Done Sprint 11+12 |
| Notification (In-app bidirectional) | Medium | ✅ **Done Sprint 21** (staff←submit, borrower←decision, link routing) |
| Notification (LINE/Email) | Low | ⏭️ Backlog |
| WebSocket / SSE (real-time แทน polling) | Low | ⏭️ Backlog |
| ปุ่ม "ส่งเอกสารเพิ่ม" บนหน้า Borrower (pending_documents flow) | Medium | ✅ **Done Sprint 22** |
| `POST /applications/{id}/cancel` (self-cancel) | Medium | ✅ **Done Sprint 13** |
| `ApplicationDetailPage.vue` (standalone) | Low | ✅ **Done Sprint 13** |
| Admin user management UI | Low | ⏭️ Backlog |
| `GET /members` + `PUT /members/{id}/financial` (staff) | Medium | ✅ **Done Sprint 13** |
| **กู้สามัญ PDF ครบ 193 fields (pages 1-5)** | **High** | ✅ **Done Sprint 14** |
| TOML-driven form schema (Dynamic Form) | Low | ⏭️ Backlog |
| OpenAPI → TypeScript codegen | Medium | ⏭️ Backlog |
| Redis + Celery (ถ้า scale ขึ้น) | Low | ⏭️ Backlog |
| Mobile-responsive improvements | Medium | Ongoing |
| Audit log archiving strategy | Low | ⏭️ Backlog |
| Virus scanning (ClamAV) บน upload pipeline | Low | ⏭️ Backlog |

---

## 🏁 Definition of Done (Final Project)

- [x] ผู้กู้สามารถยื่นคำขอและลงนามได้ครบถ้วน (Borrower flow end-to-end)
- [x] เจ้าหน้าที่สามารถพิจารณาและออกเอกสาร PDF ที่สมบูรณ์ได้
- [x] ระบบบันทึกร่องรอยการตรวจสอบ (Audit Log) ได้ถูกต้อง
- [ ] Deploy ผ่าน Docker และเข้าถึงผ่าน HTTPS ได้อย่างปลอดภัย (SSL ยังไม่ setup)

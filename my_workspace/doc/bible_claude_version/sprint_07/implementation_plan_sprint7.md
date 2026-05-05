# Implementation Plan — Sprint 7: PDF Integration & Submission

## Goal
Transform the validated web form data into a finalized, legally-compliant PDF contract and implement the submission workflow.

## User Review Required
> [!IMPORTANT]
> The PDF mapping requires 150+ fields. I will implement a robust mapping system in `pdf_service.py` based on the dictionary in `test.py`.

## Proposed Changes

### [Backend] PDF Engine & Service

#### [NEW] [pdf_engine.py](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/backend/app/engines/pdf_engine.py)
Low-level engine using `pikepdf` and `reportlab`.
- `build_field_map()`: Recursively extract AcroForm fields.
- `_make_appearance()`: Render Thai text (TH Sarabun New) as XObject.
- `_make_check_appearance()`: Render checkmarks or signatures (from bytes) as XObject.
- `fill_pdf()`: The main entry point to fill, sign, and lock (ReadOnly) the PDF.

#### [NEW] [pdf_service.py](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/backend/app/services/pdf_service.py)
High-level service for business logic.
- `fill_ordinary_loan()`: Maps `LoanOrdinaryFormData` (Steps 1-6) to the PDF field strings used by the engine.
- Handles signature data (Base64 -> Bytes).

#### [MODIFY] [application_service.py](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/backend/app/services/application_service.py)
- Implement `submit_application()`: 
    1. Validate data.
    2. Generate Application No.
    3. Generate PDF (calling `pdf_service`).
    4. Save application record to DB.
    5. Delete/Lock the draft.

### [Frontend] Validation & Submission

#### [MODIFY] [form.store.ts](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/frontend/src/stores/form.store.ts)
- Add a `validate()` action using a central Zod schema.
- Add `isSubmitting` state.

#### [NEW] [validation.ts](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/frontend/src/schemas/validation.ts)
- Define `OrdinaryLoanSchema` using `zod`.
- Thai-specific error messages.

#### [MODIFY] [FormWizard.vue](file:///F:/programming/python/MTPPR6CoopForm2/my_workspace/frontend/src/components/wizard/FormWizard.vue)
- Implement `handleSubmit()` on the final step.
- Visual feedback during submission.

## Verification Plan

### Automated Tests
- Unit tests for `pdf_engine.py` using a mock PDF.
- Backend API tests for `POST /applications`.

### Manual Verification
- Perform a full "Tablet Walk" flow.
- Download the generated PDF and verify all 15 pages (especially signatures and Thai text).

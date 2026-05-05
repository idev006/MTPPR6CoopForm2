# 16 — Sprint 6: 6-Tab Wizard & Signature Hub

---

## 16.1 Overview

In Sprint 6, we transitioned from a basic 3-step form to a comprehensive **6-tab multi-actor workflow**. This sprint focused on legal compliance (capturing all 150+ fields from the PDF) and the **"Tablet Walk"** UX, where a borrower takes their device to various stakeholders for digital signatures.

---

## 16.2 Key Features Implemented

### 1. The 6-Tab Architecture
We refactored `FormWizard.vue` to support a dynamic tab registry with role-based filtering:
1. **ข้อมูลผู้กู้:** Full profile, dual addresses, and financial status.
2. **รายละเอียดเงินกู้:** Loan amount, purpose, payout methods (Transfer/Cheque), and bank details.
3. **ผู้ค้ำประกัน:** Support for 1-3 guarantors with full ID, address, and marital status.
4. **ลงนาม (Signature Hub):** Centralized multi-actor signing center.
5. **ตรวจสอบ (Staff Only):** 18-item document checklist and financial limit analysis.
6. **สัญญา (Staff Only):** Contract numbering, interest settings, and final board approvals.

### 2. The Signature Hub (Tablet Walk Workflow)
- **Multi-Actor Support:** Integrated signing cards for Borrower, Borrower's Spouse, 1-3 Guarantors, and 1-3 Guarantor Spouses.
- **Superior Opinion:** Integrated the superior's endorsement (Page 3 of PDF) directly into the signing flow.
- **Visual Feedback:** Real-time signature previews and status indicators (✓ Signed).
- **Interactive Signature Pad:** Full-screen modal signature capture optimized for touch/stylus.

### 3. 100% PDF Compliance
We audited the 15-page legal document and added all missing fields:
- **ID Card Numbers:** Added for all parties.
- **Addresses:** Added for all guarantors.
- **Witnesses:** Added 2 signature slots in the finalization tab.
- **Payout Details:** Added bank branch, account name, and payout method toggle.

### 4. UI/UX Refinement
- **Increased Width:** Expanded the form container to `max-w-6xl` for a more professional dashboard feel.
- **Rich Aesthetics:** Used vibrant DaisyUI themes and a clean 3-column layout for density without clutter.
- **Progressive Disclosure:** Simplified marital status to "Single/Married" to focus on legal signature requirements.

---

## 16.3 Technical Changes

### Backend (Updated in Types/Schemas)
- **Types:** Updated `LoanOrdinaryFormData` to include nested `AddressInfo` and `SignatureData` for all 10+ signers.
- **Store:** Enhanced Pinia `form.store.ts` with sophisticated initialization and auto-save mapping for complex arrays.

### Frontend (Components)
- **New Components:**
    - `Step4SignatureHub.vue`
    - `Step5StaffVerification.vue`
    - `Step6ContractFinalization.vue`
    - `UiSignaturePad.vue`
- **Refactored Components:**
    - `Step1PersonalInfo.vue` (added marital logic & ID Card)
    - `Step3Guarantors.vue` (dynamic card array)
    - `AddressFields.vue` (generic re-use)

---

## 16.4 Verification Results
- [x] **Role Filtering:** Borrowers cannot see Tabs 5-6.
- [x] **Dynamic Signatures:** Spouse cards only appear if "Married" is selected.
- [x] **Data Persistence:** Auto-save correctly handles the new nested structures.
- [x] **Tablet UX:** Large signature targets and modal workflow verified.

---

## 16.5 Next Steps (Sprint 7)
- **PDF Generation Engine:** Map the web form data to the 150+ PDF fields.
- **Validation:** Add Zod validation for mandatory legal fields.
- **Submission Workflow:** Implement the final transition from "Draft" to "Submitted Application".

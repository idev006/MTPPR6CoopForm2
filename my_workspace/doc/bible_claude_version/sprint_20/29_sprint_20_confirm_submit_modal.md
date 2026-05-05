# Sprint 20 — Confirm Submit Modal

**วันที่:** 2026-04-30
**เป้าหมาย:** เพิ่ม confirmation modal ก่อนส่งคำขอ เพื่อให้ผู้กู้ตรวจสอบความพร้อมครบถ้วนก่อน submit เอกสารทางกฎหมาย

---

## ที่มาและ Problem Statement

Sprint 19 ทำ post-submit UX (success modal) แต่ไม่มี pre-submit checkpoint
ผู้กู้อาจกด "ส่งคำขอรับพิจารณา" โดยไม่ได้ดู PDF, ลายเซ็นยังขาด, หรือเอกสารแนบไม่ครบ

---

## Design Decisions

| ประเด็น | การตัดสินใจ |
|---------|------------|
| PDF ยังไม่ดู | **Block** — ปุ่มยืนยัน disabled จนกว่าจะเปิด PDF อย่างน้อย 1 ครั้ง |
| ลายเซ็นขาด | **Block** — ผู้กู้และผู้ค้ำทุกคนต้องลงนาม, ผู้บังคับบัญชาเป็น optional |
| เอกสารแนบ required ขาด | **Block** — required = payroll, id_card_borrower, house_reg_borrower, id_card_g1/g2 (ตามจำนวนผู้ค้ำ) |
| เอกสาร optional ขาด | **Warning เท่านั้น** — ไม่ block (เอกสารคู่สมรส, ฯลฯ) |
| ขนาด modal | **Scroll ใน modal** — max-h-[65vh] overflow-y-auto |

---

## Milestone Overview

```
M1 — form.store.ts         เพิ่ม pdfViewed ref + setPdfViewed()
M2 — StepReview.vue        call setPdfViewed() หลัง openPdf() สำเร็จ
M3 — attachment.service.ts เพิ่ม openFile(id) — blob URL viewer
M4 — OrdinaryLoanWizard.vue intercept @submit → confirm modal พร้อม checklist
M5 — Sprint doc + roadmap
```

---

## M1 — `pdfViewed` ใน `form.store.ts`

```typescript
const pdfViewed = ref(false)
function setPdfViewed() { pdfViewed.value = true }
// reset() ล้าง pdfViewed.value = false ด้วย
```

---

## M2 — `StepReview.vue` set pdfViewed

```typescript
async function openPdf() {
  ...
  window.open(blobUrl, '_blank')
  form.setPdfViewed()  // ← เพิ่ม
  ...
}
```

---

## M3 — `attachmentService.openFile(id)`

```typescript
async openFile(id: string): Promise<void> {
  const res = await api.get(`/attachments/${id}/download`, { responseType: 'blob' })
  const mime = res.headers['content-type'] || 'application/octet-stream'
  const url = URL.createObjectURL(new Blob([res.data], { type: mime }))
  window.open(url, '_blank')
}
```

---

## M4 — Confirm Modal ใน `OrdinaryLoanWizard.vue`

**Trigger:** `@submit="openConfirm"` แทน `@submit="form.submitForm"`

**Sections ใน modal:**
1. ⚠️ Warning banner
2. ตรวจสอบ PDF — ✅/❌ + ปุ่ม "กลับไปดู PDF" (ถ้ายังไม่ดู) หรือ "ดูอีกครั้ง"
3. ลายเซ็น — grid: ผู้กู้, ผู้บังคับบัญชา (optional), ผู้ค้ำแต่ละคน
4. เอกสารแนบ — required checklist + ไฟล์อัปโหลดพร้อมปุ่ม "ดูไฟล์ ↗"
5. ข้อมูลสำคัญ — ยอดกู้, งวด, จำนวนผู้ค้ำ
6. Blocking summary — แสดงรายการที่ยังขาด (ถ้ามี)

**canSubmit computed:**
```typescript
const canSubmit = computed(() =>
  form.pdfViewed &&
  !!form.step4.borrower_sig?.signed &&
  allGuarantorsSigned.value &&
  missingRequired.value.length === 0
)
```

**requiredDocKeys** dynamic ตามจำนวนผู้ค้ำ:
```typescript
const requiredDocKeys = computed(() => {
  const keys = ['payroll', 'id_card_borrower', 'house_reg_borrower']
  if (form.step3.guarantors.length >= 1) keys.push('id_card_g1')
  if (form.step3.guarantors.length >= 2) keys.push('id_card_g2')
  return keys
})
```

---

## Files แก้ไข

| File | Action |
|------|--------|
| `frontend/src/stores/form.store.ts` | ✏️ เพิ่ม `pdfViewed`, `setPdfViewed()` |
| `frontend/src/forms/ordinary-loan/StepReview.vue` | ✏️ call `setPdfViewed()` ใน `openPdf()` |
| `frontend/src/services/attachment.service.ts` | ✏️ เพิ่ม `openFile(id)` |
| `frontend/src/forms/ordinary-loan/OrdinaryLoanWizard.vue` | ✏️ เพิ่ม confirm modal ทั้งหมด |

---

## Definition of Done

- [x] `pdfViewed` flag ใน store — ถูก set เมื่อ `openPdf()` สำเร็จ, ถูก reset ใน `reset()`
- [x] ปุ่ม "ส่งคำขอ" เปิด confirm modal แทนการส่งทันที
- [x] modal แสดง checklist: PDF, ลายเซ็น, เอกสารแนบ required, ตัวเลขสำคัญ
- [x] ปุ่ม "ยืนยัน ส่งคำขอ" disabled ถ้า: PDF ไม่ได้ดู / ลายเซ็นขาด / required docs ขาด
- [x] Blocking summary แสดงรายการที่ยังขาดแบบ human-readable
- [x] กดดูเอกสารแนบแต่ละไฟล์ได้จาก modal (blob URL, auth required)
- [x] กด "ดูอีกครั้ง" เปิด PDF preview จากใน modal ได้
- [x] กด "กลับไปดู PDF" — ปิด modal + navigate ไป StepReview tab
- [x] modal scroll ได้ (max-h-[65vh] overflow-y-auto)
- [x] ปุ่ม ✕ / "← กลับแก้ไข" ปิด modal โดยไม่ submit

---

## Retrospective

**Technics:**
- `pdfViewed` เป็น UI state ที่ transient — ไม่เก็บ draft, ไม่เก็บ DB
  เมื่อ user reload หรือ switch session จะ reset เป็น false → ต้องดู PDF อีกครั้ง (ตั้งใจ)
- `requiredDocKeys` dynamic ตาม `guarantors.length` — ป้องกัน block ผิดพลาดเมื่อผู้กู้มีผู้ค้ำแค่ 1 คน
- Confirm modal โหลด attachments ทุกครั้งที่เปิด → ข้อมูลเป็นปัจจุบันเสมอ (ไม่ cache)
- `attachmentService.openFile()` ใช้ blob URL pattern เดียวกับ PDF preview — สม่ำเสมอ

---

## Status: ✅ DONE (2026-04-30)

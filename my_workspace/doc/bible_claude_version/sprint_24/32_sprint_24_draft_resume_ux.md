# Sprint 24 — Draft Resume UX

**วันที่:** 2026-04-30
**สถานะ:** ✅ DONE

---

## เป้าหมาย

แก้ UX gap: ผู้กู้ที่มี draft ค้างอยู่ไม่รู้ว่าจะ "ดำเนินการต่อ" ได้จากที่ไหน
ก่อนหน้านี้ต้องกด "เริ่มดำเนินการ" ซึ่งดูเหมือนเริ่มใหม่ทั้งหมด

---

## สิ่งที่เปลี่ยน

### `src/pages/DashboardPage.vue` (redesign)

**เพิ่ม draft section ด้านบน action cards:**

```
┌─────────────────────────────────────────────────┐
│ ⏱ คำขอที่ยังค้างอยู่                            │
│─────────────────────────────────────────────────│
│ [ร่าง] คำขอกู้สามัญ                             │
│ บันทึกล่าสุด: 30 เม.ย. 2569 12:30              │
│ ████░░░░ ขั้นตอนที่ 3 / 8                       │
│                  [ดำเนินการต่อ →] [ลบร่าง]      │
└─────────────────────────────────────────────────┘
```

**State เพิ่มใหม่:**
- `drafts: ref<DraftSession[]>([])` — โหลดพร้อมกับ applications บน mount
- `loadingDrafts: ref(true)`
- `discardingId: ref<string|null>(null)` — track ว่า draft ไหนกำลังถูกลบ
- `hasDrafts: computed` — ใช้ toggle header text ของ action cards

**Functions:**
- `loadDrafts()` — `Promise.allSettled` ดึงทั้ง `loan_ordinary` + `loan_emergency` พร้อมกัน
- `continueDraft(draft)` — navigate ไป wizard route ตาม `form_type` (ไม่ reset form — wizard โหลด draft จาก server เอง)
- `discardDraft(draft)` — `confirm()` → `draftService.delete()` → ลบออกจาก array + toast
- `startNew(formType)` — navigate ไป wizard (wizard โหลด draft ถ้ามี หรือสร้างใหม่)

**FORM_TYPE_META:**
```typescript
const FORM_TYPE_META = {
  loan_ordinary:  { label: 'กู้สามัญ',   route: 'application-ordinary-new', stepTotal: 8 },
  loan_emergency: { label: 'กู้ฉุกเฉิน', route: 'application-emergency-new', stepTotal: 6 },
}
```

---

## Design Decisions

### D-1: ใช้ `Promise.allSettled` โหลด drafts
- โหลด `loan_ordinary` + `loan_emergency` พร้อมกัน
- ถ้าไม่มี draft (404) → `null` → filter ออก ไม่ throw error

### D-2: `continueDraft` ไม่ต้อง reset form store
- Wizard (`OrdinaryApplicationPage.vue`) เรียก `draftService.getByFormType()` ใน `onMounted`
- ถ้ามี draft → `form.initFromDraft(existing)` โหลดข้อมูลจาก server
- ดังนั้น navigate ตรงได้เลย ไม่ต้องส่งข้อมูลผ่าน form store

### D-3: `discardDraft` ใช้ native `confirm()`
- เพื่อความเร็วในการพัฒนา ไม่ได้สร้าง modal ใหม่
- ถ้าต้องการ UX ดีกว่า → upgrade เป็น DaisyUI `<dialog>` ในอนาคต

### D-4: Progress bar แสดง `current_step / stepTotal`
- `current_step` มาจาก `DraftSession.current_step` (backend บันทึก step ล่าสุด)
- `stepTotal` hardcode ใน `FORM_TYPE_META` (loan_ordinary=8, loan_emergency=6)

### D-5: หัวข้อ Action Cards เปลี่ยนตาม draft state
- ไม่มี draft → "ยื่นคำขอกู้เงิน"
- มี draft → "เริ่มคำขอใหม่"

---

## สถานะคำขอกู้และผลต่อผู้กู้ (เอกสารอ้างอิง)

| สถานะ | ผู้กู้แก้ไขได้? | หมายเหตุ |
|---|---|---|
| `draft` | ✅ ทุกอย่าง | ยังไม่ submit ไม่มีเลขคำขอ |
| `submitted` | ❌ | ยกเลิกได้อย่างเดียว |
| `under_review` | ❌ | ทำอะไรไม่ได้ |
| `pending_documents` | ❌ แก้ฟอร์มไม่ได้ | อัปโหลดเอกสารเพิ่มได้ |
| `approved` / `rejected` / `cancelled` | ❌ | ปิดแล้ว |

---

## Flow หลังแก้ไข

```
[Dashboard โหลด]
  → loadApplications() + loadDrafts() พร้อมกัน
  → ถ้ามี draft: แสดง draft card + progress bar
  → ถ้าไม่มี: แสดงแค่ action cards

[กด "ดำเนินการต่อ"]
  → navigate ไป wizard
  → wizard onMounted: getByFormType() → initFromDraft()
  → เปิด wizard ที่ step ค้างไว้

[กด "ลบร่าง"]
  → confirm() → draftService.delete()
  → draft card หายทันที + toast
```

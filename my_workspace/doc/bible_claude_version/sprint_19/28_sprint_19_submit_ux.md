# Sprint 19 — Submit Application UX

**วันที่:** 2026-04-29
**เป้าหมาย:** ทำ UX ให้สมบูรณ์หลังผู้กู้กดปุ่ม "ส่งคำขอรับพิจารณา" — แสดง success modal พร้อมเลขคำขอ, ลบ draft, และ redirect ไป Dashboard

---

## ที่มาและ Problem Statement

Sprint 18 เพิ่ม StepReview ที่มีปุ่ม "ส่งคำขอรับพิจารณา" แต่ `form.submitForm()` ทำแค่:
1. POST ไป backend → ได้ `application_no` กลับมา
2. Set `submissionResult` ใน Pinia store
3. แสดง toast "ส่งคำขอเรียบร้อยแล้ว"

แต่ยังขาด:
- **ไม่มี success UI** — `submissionResult` ถูก set แต่ `OrdinaryApplicationPage.vue` ไม่ react กับมัน
- **Draft ยังอยู่ใน DB** — ผู้ใช้กลับมาจะเจอ draft เดิม ทำให้กรอกใหม่ไม่ได้
- **ไม่มี redirect** — ผู้ใช้ไม่รู้ว่าต้องทำอะไรต่อ

---

## Milestone Overview

```
M1 — draft_service.py     เพิ่ม delete_draft()
M2 — drafts.py            เพิ่ม DELETE /drafts/{draft_id} endpoint
M3 — draft.service.ts     เพิ่ม delete() method
M4 — form.store.ts        submitForm() ลบ draft หลัง submit สำเร็จ
M5 — OrdinaryApplicationPage.vue  success modal + redirect
```

---

## M1 — `delete_draft()` ใน `draft_service.py`

```python
async def delete_draft(draft_id: UUID, user_id: UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(DraftSession).where(
            DraftSession.id == draft_id,
            DraftSession.user_id == user_id,
        )
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise NotFoundError("ไม่พบ draft")
    await db.delete(draft)
    await db.commit()
```

---

## M2 — `DELETE /drafts/{draft_id}`

```
DELETE /api/v1/drafts/{draft_id}
Auth: Required
Response: 204 No Content
```

---

## M3 — `draftService.delete()`

```typescript
async delete(draftId: string): Promise<void> {
  await api.delete(`/drafts/${draftId}`)
},
```

---

## M4 — `submitForm()` ลบ draft

หลัง `submissionResult.value = {...}`:

```typescript
// ลบ draft หลัง submit สำเร็จ (silent — ถ้า fail ไม่สนใจ)
if (draftId.value) {
  const { draftService } = await import('@/services/draft.service')
  try { await draftService.delete(draftId.value) } catch { /* silent */ }
  draftId.value = null
}
```

---

## M5 — Success Modal ใน `OrdinaryApplicationPage.vue`

**Layout:**
```
┌──────────────────────────────────────┐
│                 ✅                    │
│     ส่งคำขอสำเร็จแล้ว!              │
│                                      │
│  หมายเลขคำขอ                         │
│  ┌──────────────────────────────┐   │
│  │  ORD-69-00001                │   │
│  └──────────────────────────────┘   │
│                                      │
│  เจ้าหน้าที่จะตรวจสอบคำขอของท่าน    │
│  และติดต่อกลับภายใน 3-5 วันทำการ   │
│                                      │
│       [ ไปยังหน้าหลัก ]             │
└──────────────────────────────────────┘
```

- **trigger**: `watch(() => form.submissionResult, result => { if (result) showModal = true })`
- **ปุ่ม "ไปยังหน้าหลัก"**: `form.reset()` แล้ว `router.push({ name: 'dashboard' })`
- **modal backdrop** ไม่ปิดได้ (ไม่มี `@click.self="close"`) — ต้องกดปุ่มเท่านั้น

---

## Files จะถูกแก้ไข

| File | Action |
|------|--------|
| `backend/app/services/draft_service.py` | ✏️ เพิ่ม `delete_draft()` |
| `backend/app/api/v1/routers/drafts.py` | ✏️ เพิ่ม `DELETE /drafts/{draft_id}` |
| `frontend/src/services/draft.service.ts` | ✏️ เพิ่ม `delete()` |
| `frontend/src/stores/form.store.ts` | ✏️ `submitForm()` ลบ draft หลัง submit |
| `frontend/src/pages/OrdinaryApplicationPage.vue` | ✏️ เพิ่ม success modal |

---

## Definition of Done

- [x] `DELETE /drafts/{draft_id}` ลบ draft ของ user นั้นออกจาก DB (403 ถ้าไม่ใช่เจ้าของ, 404 ถ้าไม่มี)
- [x] `submitForm()` เรียก `draftService.delete()` หลัง submit สำเร็จ (silent fail)
- [x] `OrdinaryApplicationPage.vue` แสดง success modal เมื่อ `form.submissionResult` ถูก set
- [x] Modal แสดงเลขคำขอ (`application_no`) อย่างชัดเจน
- [x] ปุ่ม "ไปยังหน้าหลัก" → `form.reset()` + redirect dashboard
- [x] กลับมากรอกใหม่ → draft ไม่มีแล้ว → สร้าง draft ใหม่อัตโนมัติ

---

## Status: ✅ DONE (2026-04-29)

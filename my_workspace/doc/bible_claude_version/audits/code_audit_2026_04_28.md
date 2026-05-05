# Code Audit — Frontend & Backend

**วันที่:** 2026-04-28  
**แก้ไขเมื่อ:** 2026-04-28 (Sprint 12 — same session)  
**ขอบเขต:** `my_workspace/backend/app/` และ `my_workspace/frontend/src/`  
**วิธีการ:** Static code analysis — อ่าน source โดยตรง ไม่ใช่ runtime testing  
**ผลสรุป:** พบ **19 ปัญหา** — 4 Critical, 7 High, 5 Medium, 3 Low  
**สถานะ:** ✅ แก้ครบทุกรายการแล้ว (ยกเว้น M-04 ApplicationDetailPage — ต้องสร้าง UI ใหม่)

---

## ระดับความรุนแรง

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🔴 Critical | Runtime crash หรือ security hole — ระบบใช้งานไม่ได้ / อันตราย |
| 🟠 High | Bug ที่ทำให้ feature หลักทำงานผิดพลาด |
| 🟡 Medium | ปัญหา logic หรือ data integrity ที่ไม่ crash ทันที แต่ให้ผลผิด |
| 🟢 Low | Dead code, style, minor inconsistency |

---

## 🔴 CRITICAL

---

### C-01 — `current_user` dict แต่ทุก router ใช้ dot notation → AttributeError ทุก endpoint

**ไฟล์:** `applications.py`, `attachments.py`, `staff_applications.py`

`get_current_user` ใน `dependencies.py` return เป็น **plain dict**:

```python
# dependencies.py:27
return {"id": payload["sub"], "role": payload["role"]}
```

แต่ router files อื่นๆ ใช้ dot notation ราวกับเป็น object:

```python
# applications.py:20 — type hint ผิด
current_user: User = Depends(get_current_user)
# application_service.py:29 — ใช้ user.id (AttributeError!)
applicant_id=user.id,

# attachments.py:33 — AttributeError
if app.applicant_id != current_user.id and current_user.role != "staff":

# staff_applications.py:21 — AttributeError
if user.role != "staff":
```

**ผลกระทบ:** ทุก endpoint ต่อไปนี้ crash ด้วย `500 Internal Server Error` ทันทีที่ถูกเรียก:
- `POST /applications` (submit loan)
- `POST /attachments/applications/{app_id}` (upload file)
- `GET /attachments/{att_id}/download`
- `DELETE /attachments/{att_id}`
- ทุก `GET/POST /staff/applications/*`

Endpoints ที่ใช้ `CurrentUser` annotation ถูกต้อง (auth.py, drafts.py) ทำงานได้ปกติ

**แนวทางแก้:** เปลี่ยน router ที่ผิดให้ใช้ `CurrentUser` annotation และ dict access:

```python
# ถูก
@router.post("")
async def submit_application(
    data: OrdinaryLoanSubmit,
    current_user: CurrentUser,    # ← ใช้ alias จาก dependencies.py
    db: DbSession
):
    service = ApplicationService(db)
    app = await service.submit_ordinary_loan(current_user["id"], data)  # ← dict access
```

---

### C-02 — `/system` endpoints ไม่มี authentication เลย

**ไฟล์:** `system.py`

```python
@router.get("/stats")          # ← no auth
@router.post("/clear-cache")   # ← no auth
@router.post("/backup")        # ← no auth
```

ทุก endpoint ใน `system.py` ไม่มี `Depends(get_current_user)` หรือ `StaffOnly` dependency:

- `GET /system/stats` — expose ข้อมูล `total_users`, `total_applications`, `pending_review` ให้ anonymous user
- `POST /system/clear-cache` — anonymous user ลบ generated PDFs ทั้งหมดได้
- `POST /system/backup` — anonymous user trigger backup ได้

`GET /system/config` ตั้งใจ public ไว้ (SSOT config สำหรับ frontend) แต่ควร document ชัดเจน

**แนวทางแก้:**

```python
@router.get("/stats")
async def get_system_stats(
    db: DbSession,
    current_user: StaffOnly    # ← เพิ่ม
):

@router.post("/clear-cache")
async def clear_system_cache(current_user: StaffOnly):    # ← เพิ่ม
```

---

### C-03 — `review_service.py` ใช้ `User.username` ซึ่งไม่มีใน model

**ไฟล์:** `review_service.py:39`, `review_service.py:142`

```python
# review_service.py:39
stmt = (
    select(LoanApplication, User.username)    # ← User model ไม่มี username column!
    .join(User, LoanApplication.applicant_id == User.id)
)

# review_service.py:142
logger.info(f"Staff {staff_user.username} updated App {app_id}...")    # ← AttributeError
```

`User` model มีเฉพาะ `first_name`, `last_name`, `email` ไม่มี `username`

**ผลกระทบ:** `GET /staff/applications` (list) crash ทุกครั้ง → Staff dashboard ใช้งานไม่ได้

**แนวทางแก้:**

```python
select(LoanApplication, User.first_name, User.last_name)
# ...
"applicant_name": f"{first_name} {last_name}"

# และใน log
logger.info(f"Staff {staff_user['id']} updated App {app_id}...")
```

---

### C-04 — Frontend ไม่มี session restore — ผู้ใช้ถูก logout ทุก page refresh

**ไฟล์:** `auth.store.ts`, `router/index.ts`

`accessToken` เก็บใน memory (ถูกต้องด้านความปลอดภัย) แต่ไม่มีกลไกฟื้นฟู session:

```typescript
// auth.store.ts
const accessToken = ref<string | null>(null)    // null ทุกครั้งที่ reload
const isAuthenticated = computed(() => !!accessToken.value)    // always false after reload
```

Router guard ตรวจ `auth.isAuthenticated` ก่อน → redirect to `/login` ทันที

ระบบมี refresh token ใน HttpOnly cookie อยู่แล้ว แต่ไม่มีจุดไหนที่เรียก `/auth/refresh` อัตโนมัติเมื่อ app load

**ผลกระทบ:** ผู้ใช้ต้อง login ใหม่ทุกครั้งที่ refresh browser หรือเปิด tab ใหม่

**แนวทางแก้:** เพิ่ม init function ใน `App.vue` หรือ router guard:

```typescript
// App.vue onMounted หรือ router.beforeEach
async function initAuth() {
  try {
    const res = await axios.post('/api/v1/auth/refresh', {}, { withCredentials: true })
    auth.setAuth(res.data.access_token, res.data.user)
  } catch {
    // no valid refresh token → stay logged out (normal)
  }
}
```

---

## 🟠 HIGH

---

### H-01 — Emergency Loan ไม่มี backend endpoint

**ไฟล์:** `applications.py`, `application.service.ts`

`EmergencyLoanService` มีอยู่ใน `emergency_loan_service.py` แต่ไม่มี router เรียกใช้:

```python
# applications.py — มีแค่ ordinary
@router.post("", ...)
async def submit_application(data: OrdinaryLoanSubmit, ...):
    service = ApplicationService(db)    # ← ordinary only
```

Frontend ส่งทั้ง ordinary และ emergency ไปที่ `POST /applications` เดียวกัน:

```typescript
// application.service.ts:15
const response = await api.post<SubmitResponse>('/applications', data)
```

**ผลกระทบ:** Emergency loan submit จะผ่าน ordinary flow แต่ step2 field ชื่อต่างกัน (`repayment_period` vs Zod schema ที่ validate ต่างกัน) → ข้อมูลไม่สมบูรณ์

**แนวทางแก้:** สร้าง router endpoint แยก:
```python
@router.post("/emergency", response_model=ApplicationResponse, status_code=201)
async def submit_emergency_application(data: EmergencyLoanSubmit, current_user: CurrentUser, db: DbSession):
    service = EmergencyLoanService(db)
    app = await service.create_emergency_application(UUID(current_user["id"]), data.model_dump())
    ...
```

และแยก service call ใน frontend ตาม `formType`

---

### H-02 — `application_service.py` ใช้ field key ผิด

**ไฟล์:** `application_service.py:32-33`

```python
# application_service.py:32-33
requested_amount=float(data.step2.get("loan_amount", 0)),
requested_term=int(data.step2.get("installments", 0)),    # ← 2 errors
```

**Error 1:** `"installments"` ≠ ชื่อ field จริง  
- Frontend `Step2Data` ใช้ `repayment_period`
- Zod validation.ts ใช้ `installments` (ดู H-03)
- เป็น inconsistency สามทาง → ค่าเสมอ 0

**Error 2:** `requested_term` ≠ column ใน model  
- `LoanApplication` model มี `requested_installments` ไม่มี `requested_term`
- SQLAlchemy จะ raise `InvalidRequestError` หรือ silently ignore

**แนวทางแก้:**
```python
requested_amount=float(data.step2.get("loan_amount", 0)),
requested_installments=int(data.step2.get("repayment_period", 0)),
```

---

### H-03 — `validation.ts` (Zod schema) ใช้ field keys ผิด — ไม่ตรงกับ `form.ts`

**ไฟล์:** `schemas/validation.ts`, `types/form.ts`

| Zod schema (`validation.ts`) | TypeScript type (`form.ts`) | ปัญหา |
|---|---|---|
| `step2.installments` | `Step2Data.repayment_period` | ชื่อต่างกัน |
| `step2.account_no` | `Step2Data.bank_account_no` | ชื่อต่างกัน |
| (ไม่มี `bank_account_name`) | `Step2Data.bank_account_name` | ขาด |

**ผลกระทบ:** Zod validation `ordinaryLoanSchema` ตรวจสอบ field ที่ไม่มีอยู่จริงใน store → validation ผ่านเสมอแม้ข้อมูลไม่ครบ หรือ error path ผิด

---

### H-04 — `GuarantorInfo.address` ≠ `current_addr` ที่ service คาดหวัง

**ไฟล์:** `types/form.ts:57`, `application_service.py:113`

```typescript
// form.ts — GuarantorInfo
address: AddressInfo    // ← field ชื่อ "address"
```

```python
# application_service.py:113
address_snapshot=g.get("current_addr"),    # ← คาดหวัง "current_addr"
```

**ผลกระทบ:** `address_snapshot` ของทุก guarantor เป็น `None` เสมอ — ข้อมูลที่อยู่ผู้ค้ำประกันไม่ถูก snapshot

**แนวทางแก้:** เลือกทำให้ตรงกันทั้งสองฝั่ง — `address` หรือ `current_addr` อย่างใดอย่างหนึ่ง

---

### H-05 — `attachments.py:83` — NullPointerException ถ้า app ถูกลบ (download)

**ไฟล์:** `attachments.py:79-84`

```python
result = await db.execute(stmt)
app = result.scalar_one_or_none()

# ← ไม่มี None check!
if app.applicant_id != current_user.id and current_user.role != "staff":
```

ถ้า attachment ยังอยู่แต่ LoanApplication ถูกลบ → `app` เป็น `None` → `AttributeError: 'NoneType' object has no attribute 'applicant_id'`

**แนวทางแก้:**
```python
if not app:
    raise HTTPException(status_code=404, detail="Application not found")
if app.applicant_id != current_user["id"] and current_user["role"] != "staff":
    ...
```

---

### H-06 — `system.py:46,102` — Hardcoded relative paths

**ไฟล์:** `system.py:46`, `system.py:102`

```python
# system.py:46
attachments_dir = "data/attachments"    # ← relative, ขึ้นอยู่กับ CWD

# system.py:102
db_file = "coopform_dev.db"    # ← hardcoded dev DB path!
backup_dir = "data/backups"    # ← relative
```

`DATA_DIR` มีอยู่ใน `settings` แล้ว แต่ `system.py` ไม่ใช้

**ผลกระทบ:** Stats และ backup จะ silently fail ใน production (path ผิด)

**แนวทางแก้:**
```python
from app.core.config import get_settings
settings = get_settings()
attachments_dir = Path(settings.DATA_DIR) / "attachments"
```

---

### H-07 — `notification_service.py:50-51` — `unread_only` filter ใช้ query ผิดลำดับ

**ไฟล์:** `notification_service.py:48-53`

```python
stmt = select(Notification)
    .where(Notification.user_id == user_id)
    .order_by(desc(Notification.created_at))
    .limit(limit)        # ← LIMIT ถูก apply ก่อน

if unread_only:
    stmt = stmt.where(Notification.is_read == False)    # ← WHERE เพิ่มหลัง LIMIT
```

ผล: ดึง 50 รายการล่าสุดก่อน แล้วค่อย filter unread — ถ้ามี 50 read notifications ล่าสุด จะได้ 0 unread แม้มี unread เก่ากว่า

**แนวทางแก้:** build WHERE ก่อน แล้ว `.limit()` ทีหลัง

---

## 🟡 MEDIUM

---

### M-01 — `notifications.py:45` — ไม่ตรวจ ownership ก่อน mark_as_read

**ไฟล์:** `notifications.py:38-46`

```python
@router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: UUID, db: DbSession, current_user: CurrentUser):
    service = NotificationService(db)
    await service.mark_as_read(notification_id)    # ← ไม่ตรวจว่าเป็น notif ของ current_user
```

User ใดก็ได้สามารถ mark notification ของ user อื่นเป็น read ได้ถ้ารู้ UUID

**แนวทางแก้:** เพิ่ม ownership check ใน `mark_as_read` หรือ router

---

### M-02 — `notifications.py:6-7` — Duplicate import

**ไฟล์:** `notifications.py`

```python
from app.core.database import get_db    # line 6
from app.core.database import get_db    # line 7 — ซ้ำ
```

Minor แต่ indicate copy-paste quality ของไฟล์นี้

---

### M-03 — `Step2Data.payout_method` type mismatch กับ `Step2LoanDetails.vue`

**ไฟล์:** `types/form.ts:37`, `forms/ordinary-loan/Step2LoanDetails.vue:79`

```typescript
// form.ts
payout_method: 'transfer' | 'cash'    // ← ไม่มี 'cheque'
```

```html
<!-- Step2LoanDetails.vue:79 -->
<input ... @change="update('payout_method', 'cheque')" />    <!-- ← type violation -->
```

TypeScript จะ error ถ้า strict mode เปิด — ค่า `'cheque'` ไม่อยู่ใน union type

---

### M-04 — `ApplicationDetailPage.vue` เป็น stub ว่างเปล่า

**ไฟล์:** `pages/ApplicationDetailPage.vue`

```html
<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold">รายละเอียดคำขอ</h1>
    <p class="mt-2 text-base-content/60">[ Sprint 8 — Phase 5 ]</p>
  </div>
</template>
```

Route `/applications/:id` active อยู่ในระบบ แต่ page เป็นแค่ placeholder — ผู้ใช้ที่กดดูรายละเอียดเห็น blank page พร้อม sprint label

---

### M-05 — `form.store.ts:228` — `reset()` ไม่ล้าง `stepEmergency`

**ไฟล์:** `stores/form.store.ts:224-231`

```typescript
function reset() {
    ...
    Object.assign(step1, emptyStep1()); Object.assign(step2, emptyStep2())
    Object.assign(step3, emptyStep3()); Object.assign(step4, emptyStep4())
    Object.assign(step5, emptyStep5()); Object.assign(step6, emptyStep6())
    // ← stepEmergency ไม่ถูก reset!
}
```

ถ้า user submit emergency loan แล้ว navigate กลับมาสมัครใหม่ ข้อมูลเก่าจะยังอยู่

---

## 🟢 LOW

---

### L-01 — `useAutoSave.ts` เป็น dead code

**ไฟล์:** `composables/useAutoSave.ts`

Auto-save logic ย้ายเข้า `form.store.ts` แล้ว (Sprint 5.5) แต่ `useAutoSave.ts` ยังอยู่ในโปรเจกต์ ไม่ถูก import ที่ไหน — ทำให้ developer ใหม่สับสน

---

### L-02 — `auth.py:32` — `secure=False` hardcoded

**ไฟล์:** `api/v1/routers/auth.py:32`

```python
secure=False,  # True in production (HTTPS)
```

Comment บอกว่าต้องเปลี่ยนใน production แต่ไม่ได้ผูกกับ `ENVIRONMENT` setting — ต้องจำเปลี่ยนเองก่อน deploy

**แนวทางแก้:**
```python
secure=get_settings().ENVIRONMENT == "production",
```

---

### L-03 — `review_service.py` มีเฉพาะ stub methods

**ไฟล์:** `services/review_service.py:17`

```python
# ... (existing methods) ...
```

Comment นี้บ่งบอกว่าไฟล์ถูก truncate ระหว่าง session หรือ incomplete — `update_status()`, `get_applications_for_staff()`, `get_application_detail()` มีอยู่ แต่ไม่แน่ใจว่าครบทุก method ที่วางแผนไว้

---

## สรุปภาพรวม

### Backend — สถานะจริง

| Endpoint Group | สถานะ |
|---|---|
| `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me` | ✅ ทำงานได้ |
| `GET/PUT /members/me/profile` | ✅ ทำงานได้ |
| `POST /drafts`, `GET /drafts/{type}`, `PUT /drafts/{id}` | ✅ ทำงานได้ |
| `GET /system/config` | ✅ ทำงานได้ (แต่ไม่มี auth) |
| `GET /notifications/*` | ✅ ทำงานได้ (เมื่อแก้ C-01) |
| `POST /applications` (ordinary) | ❌ 500 — C-01 + H-02 |
| `GET /applications/me` | ❌ 500 — C-01 |
| `*/attachments/*` | ❌ 500 — C-01 |
| `GET /staff/applications` (list) | ❌ 500 — C-01 + C-03 |
| `POST /staff/applications/:id/review` | ❌ 500 — C-01 + C-03 |
| `GET /system/stats` | ⚠️ ทำงานได้แต่ไม่มี auth |
| `POST /system/clear-cache` | ⚠️ ทำงานได้แต่ไม่มี auth |

### Frontend — สถานะจริง

| Feature | สถานะ |
|---|---|
| Login/Logout | ✅ ทำงานได้ |
| Profile view/edit | ✅ ทำงานได้ |
| Draft save (auto) | ✅ ทำงานได้ |
| Session after page refresh | ❌ ต้อง login ใหม่ทุกครั้ง — C-04 |
| Ordinary loan form (UI) | ✅ UI ครบ |
| Ordinary loan submit | ❌ 500 จาก backend — C-01 |
| Emergency loan submit | ❌ ไม่มี endpoint — H-01 |
| Application detail | ❌ Stub page — M-04 |

---

## Priority Action Plan

| Priority | ID | รายละเอียด | ระยะเวลาประมาณ |
|---|---|---|---|
| 🔴 1 | C-01 | แก้ `current_user` dict access ใน 3 router files | 30 นาที |
| 🔴 2 | C-02 | เพิ่ม `StaffOnly` dependency ใน system.py endpoints | 15 นาที |
| 🔴 3 | C-03 | แก้ `User.username` → `User.first_name`/`last_name` | 20 นาที |
| 🔴 4 | C-04 | เพิ่ม auth init (refresh on app load) ใน frontend | 45 นาที |
| 🟠 5 | H-01+H-02 | สร้าง emergency endpoint + แก้ field keys | 1 ชั่วโมง |
| 🟠 6 | H-03 | Sync Zod schema กับ TypeScript types | 30 นาที |
| 🟠 7 | H-04 | Align GuarantorInfo address field name | 15 นาที |
| 🟠 8 | H-05 | เพิ่ม None check ใน download endpoint | 10 นาที |
| 🟠 9 | H-06 | แก้ hardcoded paths ใน system.py | 15 นาที |
| 🟠 10 | H-07 | แก้ query order ใน notification_service | 10 นาที |
| 🟡 11 | M-01 | เพิ่ม ownership check ใน mark_as_read | 15 นาที |
| 🟡 12 | M-03 | แก้ payout_method type union | 10 นาที |
| 🟡 13 | M-05 | เพิ่ม stepEmergency ใน reset() | 5 นาที |
| 🟢 14 | L-01 | ลบ useAutoSave.ts | 5 นาที |
| 🟢 15 | L-02 | ผูก secure cookie กับ ENVIRONMENT | 5 นาที |

---

## สิ่งที่ดีและเป็น Strength

- **Auth pattern (auth.py, drafts.py):** JWT + refresh cookie + HttpOnly + SameSite ถูกต้อง
- **Rate limiting:** slowapi เพิ่มใน main.py แล้ว
- **File validation pipeline:** Architecture ดี แม้มี edge case (M ข้างบน)
- **Audit log:** `AuditLog` model + `review_service` บันทึก old/new values + IP ครบ
- **Service layer separation:** ส่วนใหญ่ถูกต้อง (ยกเว้น attachment เดิม ที่แก้แล้ว)
- **Draft system:** logic ถูกต้อง, user isolation ถูกต้อง, expiry ถูกต้อง
- **Async/await:** ใช้ถูกต้องทั้ง backend (asyncpg pattern) และ frontend
- **CORS config:** อ่านจาก security.toml ไม่ hardcode
- **Docs mode in dev only:** `docs_url="/api/docs" if is_dev else None` — ดี

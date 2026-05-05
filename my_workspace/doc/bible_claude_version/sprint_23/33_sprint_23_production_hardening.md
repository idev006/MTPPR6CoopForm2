# Sprint 23 — Production Hardening

**วันที่:** 2026-04-30
**สถานะ:** ✅ DONE

---

## เป้าหมาย

เสริมความแข็งแกร่งของระบบก่อนเปิดใช้งานจริง ครอบคลุม 4 ด้าน:
A. Rate Limiting — ป้องกัน brute force บน login
B. File Validation — ตรวจ magic bytes จริง ไม่ใช่แค่ extension
C. README.md — เอกสารสำหรับผู้ดูแลและนักพัฒนา
D. Error Pages — หน้า 404/403 แทน redirect เงียบ

---

## Definition of Done

- [ → ✅] Login เกิน 5 ครั้ง/นาที ต่อ IP → 429 Too Many Requests
- [ → ✅] Upload ไฟล์ปลอม (EXE rename เป็น PDF) → 400 Bad Request
- [ → ✅] README.md ครบ: setup, flow, credentials, security
- [ → ✅] เข้า URL ที่ไม่มี → เห็นหน้า 404 มีปุ่มกลับหน้าหลัก
- [ → ✅] Staff เข้า borrower route → เห็นหน้า 403 ไม่ใช่ redirect เงียบ

---

## สิ่งที่สร้าง / แก้ไข

### Backend

#### `app/core/limiter.py` (ใหม่)
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```
Shared limiter instance — ใช้ร่วมกันระหว่าง `main.py` และ routers

#### `app/main.py`
- เปลี่ยนจาก `Limiter(...)` inline → import จาก `app.core.limiter`
- `app.state.limiter = limiter` + `add_exception_handler(RateLimitExceeded, ...)`

#### `app/api/v1/routers/auth.py`
```python
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, body: LoginRequest, response: Response, db: DbSession):
```
- เพิ่ม `request: Request` parameter (slowapi requirement)
- เพิ่ม `@limiter.limit("5/minute")` decorator

#### `app/core/validators.py`
เพิ่ม `MagicBytesValidator` class:
```python
_ALLOWED_MAGIC = [
    (b'\x25\x50\x44\x46', 'PDF'),   # %PDF
    (b'\xff\xd8\xff',     'JPEG'),
    (b'\x89\x50\x4e\x47', 'PNG'),
]

class MagicBytesValidator(BaseValidator):
    def validate(self, header: bytes):
        for magic, label in _ALLOWED_MAGIC:
            if header[:len(magic)] == magic:
                return
        raise HTTPException(400, "ประเภทไฟล์ไม่ถูกต้อง รองรับเฉพาะ PDF, JPG, PNG เท่านั้น")
```

#### `app/services/attachment_service.py`
```python
# อ่าน 8 bytes แรก → MagicBytesValidator
header = file.file.read(8)
file.file.seek(0)
MagicBytesValidator().validate(header)
# จากนั้น seek end → วัดขนาด → FileSizeValidator + FileTypeValidator ตามเดิม
```

---

### Frontend

#### `src/pages/NotFoundPage.vue` (ใหม่)
- แสดง "404 ไม่พบหน้าที่ต้องการ"
- ปุ่ม "ย้อนกลับ" + "ไปหน้าหลัก" (route ตาม role)

#### `src/pages/ForbiddenPage.vue` (ใหม่)
- แสดง "403 ไม่มีสิทธิ์เข้าถึง"
- ปุ่ม "ย้อนกลับ" + "ไปหน้าหลัก" (route ตาม role)

#### `src/router/index.ts`
```typescript
{ path: '/403', name: 'forbidden', component: () => import('@/pages/ForbiddenPage.vue') }
{ path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/pages/NotFoundPage.vue') }
```
Route guard เปลี่ยนจาก redirect เงียบ → `{ name: 'forbidden' }` เมื่อไม่มีสิทธิ์

---

### เอกสาร

#### `my_workspace/README.md` (ใหม่)
ครอบคลุม:
- Stack overview
- Setup ครั้งแรก (venv, pip, npm, alembic, seed)
- วิธีรัน (start_dev.bat + start_tunnel.bat)
- User credentials (borrower + staff)
- Directory structure
- URL สำคัญ
- Flow การใช้งาน
- Security summary

---

## Design Decisions

### D-1: Shared Limiter Instance ผ่าน module แยก
ถ้า limiter อยู่ใน `main.py` แล้ว router import กลับ → circular import
แก้โดยแยกเป็น `app/core/limiter.py` — ทั้ง `main.py` และ router import จากที่เดียว

### D-2: Magic bytes ตรวจก่อน content-type
`file.content_type` มาจาก client — สามารถ spoof ได้
magic bytes อ่านจาก file content จริง — client แก้ไขไม่ได้
ลำดับ: MagicBytesValidator → FileTypeValidator → FileSizeValidator

### D-3: Error pages ใช้ `router.back()` + homeRoute computed
- `homeRoute` คำนวณจาก `auth.user?.role` → staff ไป `/staff`, borrower ไป `/`
- ไม่ hardcode role string ใน template

### D-4: slowapi ต้อง install ใน system Python (ไม่ใช่ venv)
Backend รันด้วย system Python (`C:\Users\66996\AppData\Local\Programs\Python\Python312\`)
ไม่ใช่ venv ที่ `F:\programming\python\MTPPR6CoopForm2\Scripts\`
ดังนั้น `python -m pip install slowapi` ต้องรันด้วย system Python

---

## หมายเหตุ (Retrospective)

⚠️ **ข้อผิดพลาด:** Sprint นี้ implement โค้ดเสร็จก่อนสร้าง Sprint Doc
ซึ่งขัดหลักการข้อ 13 "Documentation Drives Code" ใน `00_design_philosophy.md`
Sprint Doc นี้สร้างย้อนหลัง — จะไม่เกิดซ้ำใน Sprint ถัดไป

**บทเรียน:** แม้ feature ดูเหมือน "เล็ก" — ต้องเขียน Doc ก่อนเสมอ
เพราะ design decisions ที่เกิดระหว่าง coding (เช่น D-1 circular import) มีคุณค่าต่อ sprint ถัดไป

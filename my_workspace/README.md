# CoopForm — ระบบยื่นคำขอกู้เงินสหกรณ์ออนไลน์

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLAlchemy 2.0 async + SQLite |
| Frontend | Vue 3 + Pinia + TypeScript + Vite + DaisyUI v5 |
| PDF | pikepdf (fill existing template) |
| Auth | JWT (access 15min) + Refresh Token (httpOnly cookie 7d) |

---

## เริ่มต้นใช้งาน (ครั้งแรก)

### 1. สร้าง Virtual Environment

```cmd
cd F:\programming\python\MTPPR6CoopForm2
python -m venv .
```

### 2. ติดตั้ง Backend Dependencies

```cmd
call F:\programming\python\MTPPR6CoopForm2\Scripts\activate
cd my_workspace\backend
pip install -r requirements.txt
```

### 3. ติดตั้ง Frontend Dependencies

```cmd
cd F:\programming\python\MTPPR6CoopForm2\my_workspace\frontend
npm install
```

### 4. สร้างฐานข้อมูลและ Seed Data

```cmd
call F:\programming\python\MTPPR6CoopForm2\Scripts\activate
cd my_workspace\backend
alembic upgrade head
python seed.py
```

---

## รันระบบ (ทุกวัน)

### วิธีที่ 1 — รัน Local (เครือข่ายภายใน)

```
ดับเบิลคลิก: my_workspace\start_dev.bat
```

เปิด browser: http://localhost:5173

### วิธีที่ 2 — รัน + เปิดให้เข้าถึงจาก Internet

```
1. รัน start_dev.bat ก่อน
2. รัน start_tunnel.bat
3. ใช้ URL ที่ได้ (*.trycloudflare.com) ส่งให้ผู้ใช้งาน
```

> URL จะเปลี่ยนทุกครั้งที่ restart tunnel

---

## บัญชีผู้ใช้งาน (Dev/Test)

| Role | Email | Password |
|---|---|---|
| ผู้กู้ (Borrower) | borrower@coop.local | Test1234! |
| เจ้าหน้าที่ (Staff) | staff@coop.local | Test1234! |

---

## โครงสร้างโปรเจกต์

```
my_workspace/
├── backend/
│   ├── app/
│   │   ├── api/v1/routers/     # FastAPI endpoints
│   │   ├── core/               # config, security, dependencies
│   │   ├── engines/            # pdf_engine, form_engine
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response
│   │   ├── services/           # business logic
│   │   └── main.py
│   ├── config/
│   │   ├── forms/              # TOML form definitions
│   │   ├── logging.toml
│   │   ├── security.toml
│   │   ├── storage.toml
│   │   └── validation.toml
│   ├── data/
│   │   ├── attachments/        # uploaded files
│   │   └── pdfs/               # generated PDFs
│   ├── alembic/                # DB migrations
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/         # shared UI components
│   │   ├── forms/              # form wizards + steps
│   │   ├── pages/              # route pages
│   │   ├── services/           # API service layer
│   │   ├── stores/             # Pinia stores
│   │   └── router/
│   └── vite.config.ts
├── start_dev.bat               # เปิด backend + frontend
├── start_tunnel.bat            # เปิด Cloudflare tunnel
└── run_backend.bat             # helper สำหรับ start_dev.bat
```

---

## URL สำคัญ

| URL | คำอธิบาย |
|---|---|
| http://localhost:5173 | Frontend |
| http://localhost:8000/api/docs | Swagger UI (dev only) |
| http://localhost:8000/api/health | Health check |

---

## Flow การใช้งาน

```
[ผู้กู้] Login → กรอกแบบฟอร์ม → แนบเอกสาร → ลงนาม → ยื่นคำขอ
    ↓ แจ้งเตือน staff อัตโนมัติ
[Staff] Login → ตรวจสอบคำขอ → อนุมัติ / ปฏิเสธ / ขอเอกสารเพิ่ม
    ↓ แจ้งเตือน borrower อัตโนมัติ
[ผู้กู้] เห็นผล / อัปโหลดเอกสารเพิ่มแล้วส่งใหม่
```

---

## Security

- Rate limit: Login สูงสุด 5 ครั้ง/นาที ต่อ IP
- File upload: ตรวจ magic bytes (PDF/JPG/PNG) ไม่ใช่แค่ extension
- JWT: access token 15 นาที, refresh token 7 วัน (httpOnly cookie)
- HTTPS: จัดการโดย Cloudflare Tunnel อัตโนมัติ

# CoopForm — ระบบยื่นคำขอกู้เงินสหกรณ์ออนไลน์

ระบบจัดการคำขอกู้เงินแบบครบวงจร รองรับแบบฟอร์มหลายประเภท (กู้สามัญ / กู้ฉุกเฉิน) พร้อมระบบลงนาม อัปโหลดเอกสาร และสร้าง PDF อัตโนมัติ

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI · SQLAlchemy 2.0 async · SQLite |
| Frontend | Vue 3 · Pinia · TypeScript · Vite · DaisyUI v5 |
| PDF Engine | ReportLab · PyMuPDF · fillpdf |
| Auth | JWT access token (15 min) + Refresh token httpOnly cookie (7 วัน) |
| Font | THSarabunNew (ภาษาไทย) |

---

## ความต้องการของระบบ (Prerequisites)

| โปรแกรม | เวอร์ชันขั้นต่ำ | ดาวน์โหลด |
|---|---|---|
| Python | 3.11+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| Git | ใดก็ได้ | https://git-scm.com/ |

---

## ขั้นตอนการติดตั้ง (Setup)

### 1. Clone โปรเจกต์

```bash
git clone https://github.com/idev006/MTPPR6CoopForm2.git
cd MTPPR6CoopForm2
```

### 2. สร้าง Python Virtual Environment

```bash
# Windows — สร้าง venv ที่ root ของโปรเจกต์
python -m venv .

# ตรวจสอบว่าสร้างสำเร็จ (จะมีโฟลเดอร์ Scripts/, Lib/, Include/)
```

### 3. ติดตั้ง Backend Dependencies

```bash
# Windows
Scripts\activate
pip install -r my_workspace\backend\requirements.txt
```

```bash
# macOS / Linux
source bin/activate
pip install -r my_workspace/backend/requirements.txt
```

### 4. ติดตั้ง Frontend Dependencies

```bash
cd my_workspace\frontend
npm install
cd ..\..
```

### 5. ฐานข้อมูลและ Environment

**ไม่ต้องตั้งค่าเพิ่ม** — ไฟล์ `.env` และ `coopform_dev.db` อยู่ใน repo แล้ว มีข้อมูลทดสอบพร้อมใช้งาน

```
my_workspace/backend/.env          ← config สำหรับ backend
my_workspace/backend/coopform_dev.db   ← SQLite พร้อม seed data
```

> หากต้องการสร้างฐานข้อมูลใหม่ตั้งแต่ต้น:
> ```bash
> cd my_workspace\backend
> alembic upgrade head
> python seed_dev.py
> ```

---

## วิธีรัน (Start)

### วิธีที่ 1 — ดับเบิลคลิก (Windows เครื่องต้นทางเท่านั้น)

```
ดับเบิลคลิก: my_workspace\start_dev.bat
```

> ⚠️ ไฟล์ `.bat` มี hardcoded path `F:\programming\python\MTPPR6CoopForm2\`
> หากติดตั้งไว้คนละ path ให้ใช้วิธีที่ 2

---

### วิธีที่ 2 — รันด้วยคำสั่งตรง (แนะนำสำหรับเครื่องอื่น)

เปิด Terminal 2 หน้าต่าง:

**Terminal 1 — Backend**

```bash
# Windows
Scripts\activate
cd my_workspace\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# macOS / Linux
source bin/activate
cd my_workspace/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend**

```bash
cd my_workspace\frontend
npm run dev
```

---

## URL ที่ใช้งาน

| URL | คำอธิบาย |
|---|---|
| http://localhost:5173 | หน้าเว็บหลัก (Frontend) |
| http://localhost:8000/docs | Swagger UI — ทดสอบ API |
| http://localhost:8000/api/health | Health check |

---

## บัญชีทดสอบ (Dev Accounts)

| Role | Email | Password |
|---|---|---|
| ผู้กู้ (Borrower) | borrower@coop.local | Test1234! |
| เจ้าหน้าที่ (Staff) | staff@coop.local | Test1234! |

---

## โครงสร้างโปรเจกต์

```
MTPPR6CoopForm2/
├── assets/
│   ├── font/THSarabunNew/          # Thai fonts (.ttf)
│   └── icons/                      # check.png
├── my_workspace/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/v1/routers/     # FastAPI endpoints
│   │   │   ├── core/               # config, security, database
│   │   │   ├── engines/            # form_engine, pdf_engine
│   │   │   ├── models/             # SQLAlchemy ORM
│   │   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── services/           # business logic
│   │   │   └── main.py
│   │   ├── migrations/             # Alembic DB migrations
│   │   ├── tests/                  # pytest test suite
│   │   ├── .env                    # environment config (included)
│   │   ├── coopform_dev.db         # SQLite พร้อม seed data
│   │   └── requirements.txt
│   ├── config/
│   │   ├── forms/
│   │   │   ├── loan_ordinary.toml  # นิยามฟอร์มกู้สามัญ
│   │   │   └── loan_emergency.toml # นิยามฟอร์มกู้ฉุกเฉิน
│   │   ├── app.toml
│   │   ├── security.toml
│   │   └── logging.toml
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── components/         # UI components
│   │   │   ├── forms/              # form wizards (ordinary / emergency)
│   │   │   ├── pages/              # route pages
│   │   │   ├── services/           # API service layer
│   │   │   ├── stores/             # Pinia stores
│   │   │   └── router/
│   │   ├── package.json
│   │   └── vite.config.ts
│   ├── nginx/                      # Nginx config (production)
│   ├── docker-compose.yml          # Docker setup
│   ├── start_dev.bat               # Windows launcher
│   └── start_tunnel.bat            # Cloudflare tunnel
```

---

## Flow การทำงาน

```
[ผู้กู้]  Login → กรอกแบบฟอร์ม → แนบเอกสาร → ลงนาม → ยื่นคำขอ
                                                          ↓
                                              แจ้งเตือน Staff อัตโนมัติ
[Staff]  Login → ตรวจสอบคำขอ → อนุมัติ / ปฏิเสธ / ขอเอกสารเพิ่ม
                                          ↓
                              แจ้งเตือน Borrower อัตโนมัติ
[ผู้กู้]  เห็นผล → อัปโหลดเอกสารเพิ่ม → ส่งใหม่
```

---

## เชื่อมต่อจาก Internet (Cloudflare Tunnel)

```bash
# ติดตั้ง cloudflared ก่อน: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
# แล้วรัน:
my_workspace\start_tunnel.bat
```

ระบบจะแสดง URL `*.trycloudflare.com` ที่ผู้อื่นเข้าถึงได้จาก Internet โดยไม่ต้องตั้งค่า port forwarding

> URL จะเปลี่ยนทุกครั้งที่ restart tunnel

---

## รัน Tests

```bash
# Windows
Scripts\activate
cd my_workspace\backend
pytest
```

---

## Security Notes

- Rate limit: Login สูงสุด 5 ครั้ง/นาที ต่อ IP
- File upload: ตรวจ magic bytes (PDF/JPG/PNG) ไม่ใช่แค่ extension
- JWT: access token 15 นาที, refresh token 7 วัน (httpOnly cookie)
- `.env` ใน repo นี้ใช้ dev secret key เท่านั้น — **ห้ามใช้ใน production**

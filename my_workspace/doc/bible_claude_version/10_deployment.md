# 10 — Deployment & Infrastructure

---

## 10.1 Docker Architecture (3 Containers)

```
Services:
  nginx  → Reverse proxy + serve Vue SPA (port 80/443)
  api    → FastAPI + PDF engine (port 8000 internal)
  db     → PostgreSQL 16 (port 5432 internal)

Network: coopform-net (bridge)
Volume:  postgres_data (named, managed by Docker)
Mounts:  ./config, ./data/* (bind mount ไปยัง host)
```

---

## 10.2 Full Directory Structure

```
coopform2/                                 ← Git root
│
├── .gitignore                             ← ครอบคลุม data/, .env, __pycache__
├── .env.example                           ← template (commit ได้)
├── .env                                   ← secrets (gitignore!)
├── docker-compose.yml                     ← Dev
├── docker-compose.prod.yml                ← Production
├── README.md
│
├── config/                                ← BIND MOUNT ทุก container
│   ├── app.toml                           ← Main config
│   ├── logging.toml                       ← Log config
│   ├── security.toml                      ← JWT, CORS config
│   └── forms/
│       ├── loan_ordinary.toml             ← Form schema + field mapping
│       └── loan_emergency.toml            ← (อนาคต)
│
├── data/                                  ← gitignore! — ข้อมูล persistent
│   ├── postgres/                          ← Named Volume (Docker จัดการ)
│   ├── pdf_templates/                     ← BIND MOUNT → api
│   │   └── loan_ordinary_v1.pdf           ← AcroForm template
│   ├── pdf_generated/                     ← BIND MOUNT → api
│   │   └── 2568/04/
│   │       └── {uuid}.pdf
│   ├── attachments/                       ← เตรียมไว้ (ยังไม่ใช้)
│   └── logs/
│       ├── api/
│       │   ├── app.log
│       │   └── error.log
│       └── nginx/
│           ├── access.log
│           └── error.log
│
├── nginx/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── conf.d/
│       └── coopform.conf
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── migrations/
│   │   ├── env.py
│   │   └── versions/
│   │       ├── 001_initial_schema.py
│   │       └── 002_loan_tables.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_applications.py
│   │   └── test_pdf_service.py
│   └── app/
│       ├── main.py
│       ├── api/v1/routers/
│       │   ├── auth.py
│       │   ├── members.py
│       │   ├── drafts.py
│       │   ├── applications.py
│       │   └── pdf.py
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── security.py
│       │   ├── logging_setup.py
│       │   └── exceptions.py
│       ├── models/
│       ├── schemas/
│       └── services/
│           ├── auth_service.py
│           ├── member_service.py
│           ├── draft_service.py
│           ├── application_service.py
│           └── pdf_service.py
│               └── pdf_engine.py      ← pikepdf + reportlab core
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.js
    └── src/
        └── (ตาม Section 7.2)
```

---

## 10.3 docker-compose.yml (Dev)

```yaml
version: '3.9'

services:
  nginx:
    build: ./nginx
    ports:
      - "80:80"
    volumes:
      - ./config:/etc/coopform/config:ro
      - ./data/logs/nginx:/var/log/nginx
    depends_on:
      - api
    networks:
      - coopform-net

  api:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=development
    volumes:
      - ./config:/app/config:ro
      - ./data/pdf_templates:/app/data/pdf_templates:ro
      - ./data/pdf_generated:/app/data/pdf_generated
      - ./data/attachments:/app/data/attachments
      - ./data/logs/api:/app/data/logs
    depends_on:
      db:
        condition: service_healthy
    networks:
      - coopform-net

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - coopform-net

volumes:
  postgres_data:

networks:
  coopform-net:
    driver: bridge
```

---

## 10.4 Docker Persistence Strategy

| Data | Strategy | Host Path | Container Path | Survive rm? |
|------|----------|-----------|----------------|-------------|
| PostgreSQL data | Named Volume | (Docker managed) | `/var/lib/postgresql/data` | ✅ |
| PDF templates | Bind Mount | `./data/pdf_templates` | `/app/data/pdf_templates` | ✅ |
| Generated PDFs | Bind Mount | `./data/pdf_generated` | `/app/data/pdf_generated` | ✅ |
| Attachments | Bind Mount | `./data/attachments` | `/app/data/attachments` | ✅ |
| TOML configs | Bind Mount | `./config` | `/app/config` | ✅ |
| Log files | Bind Mount | `./data/logs` | `/app/data/logs` | ✅ |
| App source code | Inside Image | - | `/app` | ❌ (ตั้งใจ) |
| Python deps | Inside Image | - | `/usr/local/lib` | ❌ (ตั้งใจ) |
| Vue build | Inside nginx image | - | `/usr/share/nginx/html` | ❌ (ตั้งใจ) |

---

## 10.5 .env Template

```bash
# .env.example

# Database
DATABASE_URL=postgresql+asyncpg://coopuser:password@db:5432/coopform
POSTGRES_DB=coopform
POSTGRES_USER=coopuser
POSTGRES_PASSWORD=change_me_strong_password

# Security
SECRET_KEY=change_me_to_random_32_chars_minimum_here
REFRESH_TOKEN_SECRET=change_me_another_random_key

# App
ENVIRONMENT=production
```

---

## 10.6 Nginx Config (coopform.conf)

```nginx
server {
    listen 80;
    server_name coopform.local;

    # Vue SPA — serve static files
    root /usr/share/nginx/html;
    index index.html;

    # SPA fallback — ทุก route ที่ไม่ใช่ /api/* ให้ส่ง index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 30s;   # รอ PDF gen ได้ถึง 30 วินาที
    }

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
}
```

---

## 10.7 Backup Strategy

```bash
# backup.sh — รันทุกคืน (cron หรือ manual)

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$DATE"
mkdir -p $BACKUP_DIR

# 1. Database dump
docker exec coopform2-db-1 pg_dump -U $POSTGRES_USER $POSTGRES_DB \
  > "$BACKUP_DIR/database.sql"

# 2. Files backup
tar -czf "$BACKUP_DIR/data.tar.gz" ./data/pdf_generated ./data/attachments

# 3. Config backup  
tar -czf "$BACKUP_DIR/config.tar.gz" ./config

echo "Backup สำเร็จ: $BACKUP_DIR"

# ลบ backup เก่ากว่า 30 วัน
find ./backups -type d -mtime +30 -exec rm -rf {} +
```

---

## 10.8 Draft Cleanup (ไม่ต้องใช้ Celery)

```python
# main.py — FastAPI lifespan
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ลบ draft ที่ expired
    async with get_db() as db:
        await draft_service.delete_expired(db)
    
    yield
    # Shutdown cleanup ถ้าต้องการ

app = FastAPI(lifespan=lifespan)
```

```python
# draft_service.py
async def delete_expired(db: AsyncSession):
    stmt = delete(DraftSession).where(
        DraftSession.expires_at < datetime.utcnow()
    )
    result = await db.execute(stmt)
    await db.commit()
    logger.info(f"Cleaned up {result.rowcount} expired drafts")
```

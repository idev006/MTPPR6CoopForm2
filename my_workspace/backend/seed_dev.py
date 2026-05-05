"""
สร้าง test users สำหรับ development

รันจาก my_workspace/backend/:

  SQLite (default):
    PYTHONUTF8=1 DATABASE_URL="sqlite+aiosqlite:///./coopform_dev.db" python seed_dev.py

  PostgreSQL (ต้อง alembic upgrade head ก่อน):
    PYTHONUTF8=1 DATABASE_URL="postgresql+asyncpg://coopuser:coopdev123@localhost:5432/coopform" python seed_dev.py

หรือใช้ setup_postgres.bat ซึ่งจัดการทุกขั้นตอนให้อัตโนมัติ
"""

import asyncio
import sys
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, ".")

from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User


SEED_USERS = [
    {
        "email": "borrower@coop.local",
        "password": "Test1234!",
        "role": "borrower",
        "member_code": "100001",
        "first_name": "สมชาย",
        "last_name": "รักชาติ",
    },
    {
        "email": "staff@coop.local",
        "password": "Test1234!",
        "role": "staff",
        "member_code": None,
        "first_name": "สมหญิง",
        "last_name": "ใจดี",
    },
]


async def seed():
    db_url = os.environ.get("DATABASE_URL", "")
    is_sqlite = "sqlite" in db_url

    if is_sqlite:
        # SQLite dev: create tables automatically (Alembic not required)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[info] SQLite — ตาราง create_all() เรียบร้อย")
    else:
        # PostgreSQL: ตาราง ต้องสร้างด้วย alembic upgrade head ก่อน
        print("[info] PostgreSQL — ข้าม create_all() (ใช้ alembic)")

    async with AsyncSessionLocal() as db:
        for data in SEED_USERS:
            exists = await db.execute(select(User).where(User.email == data["email"]))
            if exists.scalar_one_or_none():
                print(f"[skip] {data['email']} มีอยู่แล้ว")
                continue

            user = User(
                email=data["email"],
                hashed_password=hash_password(data["password"]),
                role=data["role"],
                member_code=data["member_code"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                is_active=True,
            )
            db.add(user)
            await db.commit()
            print(f"[ok]   สร้าง {data['role']}: {data['email']} / {data['password']}")

    print()
    print("✓ Seed เสร็จแล้ว")


if __name__ == "__main__":
    asyncio.run(seed())

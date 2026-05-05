import os
# Set test env vars BEFORE any app imports so lru_cache picks them up
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./coopform_test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-must-be-32-chars!!")
os.environ.setdefault("REFRESH_TOKEN_SECRET", "test-refresh-secret-32-chars!!!")
os.environ.setdefault("ENVIRONMENT", "test")

import uuid
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession,
    create_async_engine, async_sessionmaker,
)

from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User

TEST_DB_URL = "sqlite+aiosqlite:///./coopform_test.db"


@pytest_asyncio.fixture
async def test_engine() -> AsyncEngine:
    """Fresh SQLite DB per test — create tables, yield engine, drop tables."""
    engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncSession:
    """Session used only for fixture setup (seeding users, etc.)."""
    factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession,
        expire_on_commit=False, autoflush=False,
    )
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_engine: AsyncEngine):
    """
    HTTP test client. Each request gets a FRESH session from the test engine
    so a rollback in one request cannot poison the next request.
    """
    factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession,
        expire_on_commit=False, autoflush=False,
    )

    async def _override():
        async with factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def borrower_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="borrower@test.local",
        hashed_password=hash_password("Test1234!"),
        role="borrower",
        first_name="สมชาย",
        last_name="ใจดี",
        member_code="T001",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def staff_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="staff@test.local",
        hashed_password=hash_password("Test1234!"),
        role="staff",
        first_name="ทดสอบ",
        last_name="เจ้าหน้าที่",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def borrower_token(borrower_user: User) -> str:
    return create_access_token(str(borrower_user.id), "borrower")


@pytest_asyncio.fixture
async def staff_token(staff_user: User) -> str:
    return create_access_token(str(staff_user.id), "staff")

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings, get_app_config


def _build_engine():
    settings = get_settings()
    cfg = get_app_config().get("database", {})
    url = settings.DATABASE_URL
    is_sqlite = url.startswith("sqlite")
    kwargs: dict = {"echo": cfg.get("echo_sql", False)}
    if not is_sqlite:
        # pool settings ใช้ได้กับ PostgreSQL เท่านั้น
        kwargs["pool_size"] = cfg.get("pool_size", 5)
        kwargs["max_overflow"] = cfg.get("max_overflow", 10)
    else:
        # SQLite ต้องการ check_same_thread=False เมื่อใช้ async
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_async_engine(url, **kwargs)


engine = _build_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

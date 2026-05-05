import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from app.core.database import engine, Base
import app.models  # Import models to register them with Base

async def init_models():
    async with engine.begin() as conn:
        # For development, we just create all. In production, use Alembic.
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_models())

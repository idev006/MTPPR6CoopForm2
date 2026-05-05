from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

from app.core.config import get_settings, get_security_config
from app.core.exceptions import http_exception_handler
from app.core.logging_setup import setup_logging
from app.api.v1.routers import auth, members, drafts, applications, staff_applications, attachments, pdf, system, notifications, forms


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("CoopForm API starting up...")

    # cleanup expired drafts on startup
    try:
        from app.core.database import AsyncSessionLocal
        from app.services.draft_service import delete_expired_drafts
        async with AsyncSessionLocal() as db:
            deleted = await delete_expired_drafts(db)
            if deleted:
                logger.info(f"Cleaned up {deleted} expired drafts")
    except Exception as e:
        logger.warning(f"Draft cleanup skipped: {e}")

    yield
    logger.info("CoopForm API shutting down...")


def create_app() -> FastAPI:
    settings = get_settings()
    is_dev = settings.ENVIRONMENT == "development"

    app = FastAPI(
        title="CoopForm API",
        version="1.0.0",
        description="ระบบกรอกแบบฟอร์มขอกู้เงินสหกรณ์ออนไลน์",
        docs_url="/api/docs" if is_dev else None,
        redoc_url="/api/redoc" if is_dev else None,
        openapi_url="/api/openapi.json" if is_dev else None,
        lifespan=lifespan,
    )

    # rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS
    cors_cfg = get_security_config().get("cors", {})
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_cfg.get("allow_origins", []),
        allow_credentials=cors_cfg.get("allow_credentials", True),
        allow_methods=cors_cfg.get("allow_methods", ["*"]),
        allow_headers=cors_cfg.get("allow_headers", ["*"]),
    )

    # exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)

    # routers
    PREFIX = "/api/v1"
    app.include_router(auth.router, prefix=PREFIX)
    app.include_router(members.router, prefix=PREFIX)
    app.include_router(drafts.router, prefix=PREFIX)
    app.include_router(applications.router, prefix=PREFIX)
    app.include_router(staff_applications.router, prefix=PREFIX)
    app.include_router(attachments.router, prefix=PREFIX)
    app.include_router(system.router, prefix=PREFIX)
    app.include_router(pdf.router, prefix=PREFIX)
    app.include_router(notifications.router, prefix=f"{PREFIX}/notifications", tags=["notifications"])
    app.include_router(forms.router, prefix=PREFIX)

    @app.get("/api/health", tags=["system"])
    async def health():
        return {"status": "ok", "service": "CoopForm API"}

    return app


app = create_app()

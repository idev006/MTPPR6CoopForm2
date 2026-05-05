from fastapi import APIRouter, Cookie, Request, Response
from jose import JWTError

from app.core.config import get_security_config, get_settings
from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import UnauthorizedError
from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import authenticate_user, get_user_by_id

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE = "refresh_token"
_COOKIE_PATH = "/api/v1/auth"


def _jwt_cfg() -> dict:
    return get_security_config().get("jwt", {})


def _set_refresh_cookie(response: Response, token: str) -> None:
    cfg = _jwt_cfg()
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=token,
        httponly=True,
        samesite="strict",
        secure=get_settings().ENVIRONMENT == "production",
        max_age=cfg.get("refresh_token_expire_days", 7) * 86_400,
        path=_COOKIE_PATH,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, body: LoginRequest, response: Response, db: DbSession):
    user = await authenticate_user(body.email, body.password, db)
    if not user:
        raise UnauthorizedError("อีเมลหรือรหัสผ่านไม่ถูกต้อง")

    cfg = _jwt_cfg()
    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))
    _set_refresh_cookie(response, refresh_token)

    return TokenResponse(
        access_token=access_token,
        expires_in=cfg.get("access_token_expire_minutes", 15) * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh")
async def refresh(
    response: Response,
    db: DbSession,
    refresh_token: str | None = Cookie(default=None, alias=_REFRESH_COOKIE),
):
    if not refresh_token:
        raise UnauthorizedError()
    try:
        payload = decode_refresh_token(refresh_token)
    except JWTError:
        raise UnauthorizedError("Refresh token ไม่ถูกต้องหรือหมดอายุ")
    if payload.get("type") != "refresh":
        raise UnauthorizedError()

    user = await get_user_by_id(payload["sub"], db)
    if not user or not user.is_active:
        raise UnauthorizedError()

    cfg = _jwt_cfg()
    new_access = create_access_token(str(user.id), user.role)
    new_refresh = create_refresh_token(str(user.id))
    _set_refresh_cookie(response, new_refresh)

    return {
        "access_token": new_access,
        "token_type": "bearer",
        "expires_in": cfg.get("access_token_expire_minutes", 15) * 60,
        "user": UserResponse.model_validate(user).model_dump(),
    }


@router.post("/logout", status_code=204)
async def logout(response: Response):
    response.delete_cookie(key=_REFRESH_COOKIE, path=_COOKIE_PATH)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser, db: DbSession):
    user = await get_user_by_id(current_user["id"], db)
    if not user or not user.is_active:
        raise UnauthorizedError()
    return UserResponse.model_validate(user)

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Cookie
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict:
    if not credentials:
        raise UnauthorizedError()
    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError:
        raise UnauthorizedError("Token ไม่ถูกต้องหรือหมดอายุ")
    if payload.get("type") != "access":
        raise UnauthorizedError()
    return {"id": payload["sub"], "role": payload["role"]}


def require_role(*roles: str):
    async def _check(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
        if current_user["role"] not in roles:
            raise ForbiddenError()
        return current_user
    return _check


CurrentUser = Annotated[dict, Depends(get_current_user)]
StaffOnly = Annotated[dict, Depends(require_role("staff"))]
DbSession = Annotated[AsyncSession, Depends(get_db)]

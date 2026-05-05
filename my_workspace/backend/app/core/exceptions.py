from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class CoopFormError(HTTPException):
    """Base exception — ส่งกลับเป็น RFC 7807 Problem Detail"""


class NotFoundError(CoopFormError):
    def __init__(self, detail: str = "ไม่พบข้อมูล"):
        super().__init__(status_code=404, detail=detail)


class ForbiddenError(CoopFormError):
    def __init__(self, detail: str = "ไม่มีสิทธิ์เข้าถึง"):
        super().__init__(status_code=403, detail=detail)


class UnauthorizedError(CoopFormError):
    def __init__(self, detail: str = "กรุณาเข้าสู่ระบบ"):
        super().__init__(status_code=401, detail=detail)


class ConflictError(CoopFormError):
    def __init__(self, detail: str = "ข้อมูลซ้ำกัน"):
        super().__init__(status_code=409, detail=detail)


class ValidationError(CoopFormError):
    def __init__(self, detail: str = "ข้อมูลไม่ถูกต้อง"):
        super().__init__(status_code=422, detail=detail)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """RFC 7807 Problem Detail format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": f"https://coopform.local/errors/{exc.status_code}",
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": str(request.url),
        },
    )

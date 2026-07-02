from fastapi import Request
from fastapi.responses import JSONResponse

from backend.core.logger import get_logger


logger = get_logger(__name__)


class AIOSException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code


async def aios_exception_handler(request: Request, exc: AIOSException):
    logger.error(f"AIOS error: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "path": str(request.url.path),
        },
    )
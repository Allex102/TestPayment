from fastapi import Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import CoreException


async def exception_handler(
    request: Request,
    exc: CoreException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )

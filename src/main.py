from fastapi import Depends, FastAPI

from src.domain.exceptions import CoreException
from src.presentation.handlers.exceptions import exception_handler
from src.presentation.routers.payment import router as payment_router
from src.utils.verification import verify_api_key

app = FastAPI(
    title="Test Payment",
    version="0.0.1",
    description=(
        "API for matching users by interests. "
        "Authentication via JWT tokens (Bearer token in header)."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    dependencies=[Depends(verify_api_key)],
)

app.include_router(
    payment_router,
    prefix="/api",
    tags=["payments"],
)

app.add_exception_handler(CoreException, exception_handler)

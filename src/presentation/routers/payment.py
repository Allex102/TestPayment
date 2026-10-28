from fastapi import APIRouter

from src.presentation.api.payment.payment import router as payment

router = APIRouter()

router.include_router(payment, prefix="/v1", tags=["payments"])

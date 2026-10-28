from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, Header

from src.application.dto.payment import PaymentCreateRequestDTO
from src.application.use_cases.payment.create import CreatePaymentUseCase
from src.application.use_cases.payment.get import GetPaymentUseCase
from src.infrastructure.query.repositories.payment import SQLAlchemyPaymentRepository
from src.presentation.dependencies.payment import get_payment_repo
from src.presentation.schemas.payment.request import PaymentCreateRequest
from src.presentation.schemas.payment.response import (
    PaymentCreateResponse,
    PaymentGetResponse,
)

router = APIRouter(tags=["payments"])


@router.post(
    "/payments",
    response_model=PaymentCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create new payment",
    description="Создать платеж",
    responses={
        409: {"description": "Conflict: payment already exists"},
        422: {"description": "Validation error"},
    },
)
async def create_payment(
    body: PaymentCreateRequest,
    repo: Annotated[
        SQLAlchemyPaymentRepository,
        Depends(get_payment_repo),
    ],
    idempotency_key: Annotated[
        str,
        Header(alias="Idempotency-Key", min_length=1, max_length=255),
]) -> PaymentCreateResponse:

    use_case = CreatePaymentUseCase(payment_repo=repo)

    dto = PaymentCreateRequestDTO(**body.model_dump())

    result = await use_case.execute(dto, idempotency_key=idempotency_key)

    return PaymentCreateResponse(**result.model_dump())

@router.get(
    "/payments/{id}",
    response_model=PaymentGetResponse,
    status_code=status.HTTP_200_OK,
    summary="Get payment details",
    description="Детальная информация о платеже",
    responses={
        404: {"description": "Payment not found"},
    },
)
async def get_payment(
    payment_id: UUID,
    repo: Annotated[
        SQLAlchemyPaymentRepository,
        Depends(get_payment_repo),
    ]
) -> PaymentGetResponse:
    use_case = GetPaymentUseCase(payment_repo=repo)

    payment = await use_case.execute(payment_id=payment_id)

    return PaymentGetResponse.model_validate(payment)

from uuid import uuid4

from src.application.dto.payment import (
    PaymentCreateRequestDTO,
    PaymentCreateResponseDTO,
)
from src.application.interfaces.repositories.payment import PaymentRepository
from src.domain.entities.payment import Payment
from src.domain.exceptions import PaymentAlreadyExistException
from src.domain.value_objects.enum import Status


class CreatePaymentUseCase:
    def __init__(self, payment_repo: PaymentRepository):
        self._payment_repo = payment_repo

    async def execute(
        self,
        request: PaymentCreateRequestDTO,
        idempotency_key: str,
    ) -> PaymentCreateResponseDTO:
        payment = (
            await self._payment_repo.get_by_idempotency_key(
                idempotency_key=idempotency_key
            )
        )

        if payment:
            raise PaymentAlreadyExistException(f"Платеж с ключем {idempotency_key} уже существует")

        payment = Payment(
            id=uuid4(),
            payment_sum=request.payment_sum,
            currency=request.currency,
            description=request.description,
            meta=request.meta,
            status=Status.PENDING,
            idempotency_key=idempotency_key,
            hook_url=str(request.hook_url) if request.hook_url else None,
        )

        payment = await self._payment_repo.create_with_outbox(payment)

        return PaymentCreateResponseDTO(
            payment_id=payment.id,
            status=payment.status,
            created_at=payment.created_at
        )
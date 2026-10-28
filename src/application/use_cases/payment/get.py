from uuid import UUID

from src.application.dto.payment.response import PaymentGetResponseDTO
from src.application.interfaces.repositories.payment import PaymentRepository
from src.application.mappers.payment import PaymentMapper
from src.domain.exceptions import PaymentNotExistException


class GetPaymentUseCase:
    def __init__(self, payment_repo: PaymentRepository):
        self._payment_repo = payment_repo

    async def execute(self, payment_id: UUID) -> PaymentGetResponseDTO:
        payment = await self._payment_repo.get_by_id(payment_id=payment_id)

        if not payment:
            raise PaymentNotExistException(f"Платеж {payment_id} не существует")

        return PaymentMapper.to_response(payment=payment)
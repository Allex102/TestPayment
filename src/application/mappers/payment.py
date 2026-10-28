from src.domain.entities.payment import Payment
from src.application.dto.payment.response import (
    PaymentGetResponseDTO
)


class PaymentMapper:
    @staticmethod
    def to_response(payment: Payment) -> PaymentGetResponseDTO:
        return PaymentGetResponseDTO(
            payment_id=payment.id,
            payment_sum=payment.payment_sum,
            currency=payment.currency,
            description=payment.description,
            meta=payment.meta,
            status=payment.status,
            hook_url=payment.hook_url
        )

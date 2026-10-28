from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

from src.application.dto.payment import PaymentCreateRequestDTO

if TYPE_CHECKING:
    from src.domain.entities.payment import Payment

class PaymentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        pass

    @abstractmethod
    async def create(self, payment_data: PaymentCreateRequestDTO) -> Payment:
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        pass

    @abstractmethod
    async def create_with_outbox(self, payment: Payment) -> Payment:
        pass
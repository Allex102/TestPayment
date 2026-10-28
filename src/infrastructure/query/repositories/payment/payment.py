from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.payment import PaymentRepository
from src.domain.entities.payment import OutboxEvent, Payment


class SQLAlchemyPaymentRepository(PaymentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        result = await self._session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def create(self, payment: Payment) -> Payment:
        self._session.add(payment)
        await self._session.flush()
        await self._session.refresh(payment)
        return payment

    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        result = await self._session.execute(
            select(Payment).where(Payment.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def create_with_outbox(self, payment: Payment) -> Payment:
        event = OutboxEvent(
            event_type="payments.new",
            aggregate_id=payment.id,
            payload={
                "payment_id": str(payment.id),
                "payment_sum": str(payment.payment_sum),
                "currency": payment.currency.value,
                "description": payment.description,
                "meta": payment.meta,
                "hook_url": payment.hook_url,
            },
        )

        self._session.add_all([payment, event])
        await self._session.flush()
        await self._session.refresh(payment)

        return payment
import asyncio
import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

import httpx
from sqlalchemy import and_, or_, select

from src.domain.entities.payment.webhook_delivery import WebhookDelivery
from src.infrastructure.query.db_engine import async_session

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5
PROCESSING_LEASE_SECONDS = 60
POLL_INTERVAL_SECONDS = 1


async def claim_delivery():
    now = datetime.now(UTC)

    eligible = or_(
        and_(
            WebhookDelivery.status == "pending",
            or_(
                WebhookDelivery.next_attempt_at.is_(None),
                WebhookDelivery.next_attempt_at <= now,
            ),
        ),
        and_(
            WebhookDelivery.status == "processing",
            WebhookDelivery.next_attempt_at <= now,
        ),
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(WebhookDelivery)
                .where(eligible)
                .order_by(WebhookDelivery.created_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            delivery = result.scalar_one_or_none()

            if delivery is None:
                return None

            delivery.status = "processing"
            delivery.attempts += 1
            delivery.next_attempt_at = now + timedelta(
                seconds=PROCESSING_LEASE_SECONDS
            )

            claimed = {
                "id": delivery.id,
                "hook_url": delivery.hook_url,
                "payload": delivery.payload,
                "attempts": delivery.attempts,
            }

        return claimed


async def update_delivery(
    delivery_id: UUID,
    *,
    success: bool,
    error: str | None = None,
    attempts: int,
) -> None:
    now = datetime.now(UTC)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(WebhookDelivery)
                .where(WebhookDelivery.id == delivery_id)
                .with_for_update()
            )
            delivery = result.scalar_one_or_none()

            if delivery is None:
                return

            if success:
                delivery.status = "delivered"
                delivery.delivered_at = now
                delivery.next_attempt_at = None
                delivery.last_error = None
                return

            delivery.last_error = (error or "Unknown error")[:2000]

            if attempts >= MAX_ATTEMPTS:
                delivery.status = "failed"
                delivery.next_attempt_at = None
                logger.error(
                    "Webhook %s failed permanently after %s attempts",
                    delivery_id,
                    attempts,
                )
                return

            delay_seconds = min(30 * (2 ** (attempts - 1)), 3600)
            delivery.status = "pending"
            delivery.next_attempt_at = now + timedelta(
                seconds=delay_seconds
            )


async def deliver_one(client: httpx.AsyncClient) -> bool:
    delivery = await claim_delivery()

    if delivery is None:
        return False

    delivery_id = delivery["id"]

    try:
        response = await client.post(
            delivery["hook_url"],
            json=delivery["payload"],
            headers={
                "X-Webhook-Delivery": str(delivery_id),
                "Idempotency-Key": str(delivery_id),
            },
        )
        response.raise_for_status()

    except Exception as exc:
        logger.error(  # noqa: G201
            "Webhook delivery %s failed; exception_type=%s, repr=%r",
            delivery_id,
            type(exc).__name__,
            exc,
            exc_info=True,
        )

        await update_delivery(
            delivery_id,
            success=False,
            error=f"{type(exc).__name__}: {exc!r}",
            attempts=delivery["attempts"],
        )
    else:
        await update_delivery(
            delivery_id,
            success=True,
            attempts=delivery["attempts"],
        )
        logger.info("Webhook delivery %s succeeded", delivery_id)

    return True


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    async with httpx.AsyncClient(timeout=10.0) as client:
        logger.info("Webhook worker started")

        while True:
            try:
                processed = await deliver_one(client)
                if not processed:
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Webhook worker iteration failed")
                await asyncio.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())

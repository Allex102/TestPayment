import asyncio
import json
import logging
import random
from uuid import UUID

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from sqlalchemy import select

from src.config.base import rabbitmq_settings
from src.domain.entities.payment.payment import Payment
from src.domain.entities.payment.webhook_delivery import WebhookDelivery
from src.domain.value_objects.enum import Status
from src.infrastructure.query.db_engine import async_session

logger = logging.getLogger(__name__)

QUEUE_NAME = "payments.new"
RETRY_QUEUE = "payments.retry"
DLQ_NAME = "payments.dlq"

MAX_ATTEMPTS = 3
RETRY_DELAY_MS = 2000


async def process_payment(body: bytes) -> None:
    payload = json.loads(body)
    payment_id = UUID(payload["payment_id"])

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Payment)
                .where(Payment.id == payment_id)
                .with_for_update()
            )
            payment = result.scalar_one_or_none()

            if payment is None:
                raise ValueError(
                    f"Payment {payment_id} not found"
                )

            if payment.status != Status.PENDING:
                logger.info(
                    "Skipping duplicate message: payment=%s, status=%s",
                    payment.id,
                    payment.status.value,
                )
                return

            await asyncio.sleep(random.uniform(2, 5))

            payment.status = (
                Status.SUCCESS
                if random.random() < 0.9
                else Status.FAILED
            )

            if payment.hook_url:
                delivery = WebhookDelivery(
                    payment_id=payment.id,
                    hook_url=payment.hook_url,
                    payload={
                        "event": "payment.status_changed",
                        "payment_id": str(payment.id),
                        "status": payment.status.value,
                    },
                    status="pending",
                    attempts=0,
                )
                session.add(delivery)

            logger.info(
                "Payment %s processed with status %s",
                payment.id,
                payment.status.value,
            )


async def route_failed_message(
    message: AbstractIncomingMessage,
    channel: aio_pika.abc.AbstractChannel,
) -> None:
    headers = dict(message.headers or {})
    retry_count = int(headers.get("x-retry-count", 0))
    next_count = retry_count + 1

    if next_count >= MAX_ATTEMPTS:
        target_queue = DLQ_NAME
        logger.error(
            "Message moved to DLQ after %s attempts",
            next_count,
        )
    else:
        target_queue = RETRY_QUEUE
        logger.warning(
            "Scheduling retry %s/%s",
            next_count,
            MAX_ATTEMPTS,
        )

    headers["x-retry-count"] = next_count

    retry_message = aio_pika.Message(
        body=message.body,
        headers=headers,
        message_id=message.message_id,
        content_type=message.content_type or "application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )

    await channel.default_exchange.publish(
        retry_message,
        routing_key=target_queue,
        mandatory=True,
    )
    await message.ack()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    connection = await aio_pika.connect_robust(
        rabbitmq_settings.RABBITMQ_URL
    )

    try:
        channel = await connection.channel(publisher_confirms=True)
        await channel.set_qos(prefetch_count=1)

        await channel.declare_queue(QUEUE_NAME, durable=True)

        await channel.declare_queue(
            RETRY_QUEUE,
            durable=True,
            arguments={
                "x-message-ttl": RETRY_DELAY_MS,
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": QUEUE_NAME,
            },
        )

        await channel.declare_queue(DLQ_NAME, durable=True)

        queue = await channel.get_queue(QUEUE_NAME)

        async def on_message(message: AbstractIncomingMessage) -> None:
            try:
                await process_payment(message.body)
            except Exception:
                logger.exception("Payment processing failed")

                try:
                    await route_failed_message(message, channel)
                except Exception:
                    logger.exception("Failed to route message for retry/DLQ")
                    await message.nack(requeue=True)
            else:
                await message.ack()

        await queue.consume(on_message, no_ack=False)

        logger.info("Payment consumer started; queue=%s", QUEUE_NAME)
        await asyncio.Future()

    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
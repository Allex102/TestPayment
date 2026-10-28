import asyncio
import json
import logging
from datetime import UTC, datetime

from sqlalchemy import select

from src.domain.entities.payment.outbox_event import OutboxEvent
from src.infrastructure.messaging.rabbitmq import RabbitMQClient
from src.infrastructure.query.db_engine import async_session

logger = logging.getLogger(__name__)

POLL_INTERVAL = 1.0


async def publish_one(client: RabbitMQClient) -> bool:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(OutboxEvent)
                .where(OutboxEvent.published_at.is_(None))
                .order_by(OutboxEvent.created_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )

            event = result.scalar_one_or_none()

            if event is None:
                return False

            try:
                body = json.dumps(
                    event.payload,
                    ensure_ascii=False,
                    default=str,
                ).encode("utf-8")

                await client.publish(
                    body,
                    event_id=str(event.id),
                    event_type=event.event_type,
                )

            except Exception as exc:
                event.attempts += 1
                event.last_error = str(exc)[:2000]

                logger.exception(
                    "Failed to publish outbox event %s",
                    event.id,
                )

            else:
                event.published_at = datetime.now(UTC)
                event.attempts += 1
                event.last_error = None

                logger.info(
                    "Published outbox event %s",
                    event.id,
                )

    return True


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = RabbitMQClient()
    await client.connect()

    try:
        while True:
            try:
                processed = await publish_one(client)

                if not processed:
                    await asyncio.sleep(POLL_INTERVAL)

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception("Outbox publisher iteration failed")
                await asyncio.sleep(POLL_INTERVAL)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
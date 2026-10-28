import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel

from src.config.base import rabbitmq_settings


QUEUE_NAME = "payments.new"


class RabbitMQClient:
    def __init__(self) -> None:
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(
            rabbitmq_settings.RABBITMQ_URL
        )

        self._channel = await self._connection.channel(
            publisher_confirms=True,
            on_return_raises=True,
        )

        await self._channel.declare_queue(
            QUEUE_NAME,
            durable=True,
        )

    async def publish(
        self,
        body: bytes,
        *,
        event_id: str,
        event_type: str,
    ) -> None:
        if self._channel is None:
            raise RuntimeError("RabbitMQ client is not connected")

        message = aio_pika.Message(
            body=body,
            message_id=event_id,
            type=event_type,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self._channel.default_exchange.publish(
            message,
            routing_key=QUEUE_NAME,
            mandatory=True,
        )

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
            self._channel = None
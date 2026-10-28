import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.domain.entities.payment.webhook_delivery import WebhookDelivery
from src.domain.value_objects.enum import Status
from src.infrastructure.messaging import payment_consumer as consumer


def make_session_context(payment):
    session = MagicMock()

    result = MagicMock()
    result.scalar_one_or_none.return_value = payment
    session.execute = AsyncMock(return_value=result)

    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=session)
    session_context.__aexit__ = AsyncMock(return_value=None)

    transaction_context = MagicMock()
    transaction_context.__aenter__ = AsyncMock(return_value=None)
    transaction_context.__aexit__ = AsyncMock(return_value=None)

    session.begin.return_value = transaction_context

    return session_context, session


def make_message(payment_id):
    return json.dumps({"payment_id": str(payment_id)}).encode()


@pytest.mark.parametrize("status", [Status.SUCCESS, Status.FAILED])
async def test_completed_payment_is_not_processed_again(monkeypatch, status):
    payment = SimpleNamespace(
        id=uuid4(),
        status=status,
        hook_url="https://example.com/webhook",
    )
    session_context, session = make_session_context(payment)

    monkeypatch.setattr(
        consumer,
        "async_session",
        lambda: session_context,
    )

    await consumer.process_payment(make_message(payment.id))

    assert payment.status == status
    session.add.assert_not_called()


async def test_pending_payment_is_processed_and_webhook_created(monkeypatch):
    payment = SimpleNamespace(
        id=uuid4(),
        status=Status.PENDING,
        hook_url="https://example.com/webhook",
    )
    session_context, session = make_session_context(payment)

    monkeypatch.setattr(
        consumer,
        "async_session",
        lambda: session_context,
    )
    monkeypatch.setattr(
        consumer,
        "asyncio",
        SimpleNamespace(sleep=AsyncMock()),
    )
    monkeypatch.setattr(
        consumer,
        "random",
        SimpleNamespace(uniform=lambda *_: 2, random=lambda: 0.1),
    )

    await consumer.process_payment(make_message(payment.id))

    assert payment.status == Status.SUCCESS
    session.add.assert_called_once()

    delivery = session.add.call_args.args[0]
    assert isinstance(delivery, WebhookDelivery)
    assert delivery.payment_id == payment.id
    assert delivery.hook_url == payment.hook_url
    assert delivery.status == "pending"
    assert delivery.attempts == 0
    assert delivery.payload["event"] == "payment.status_changed"
    assert delivery.payload["status"] == Status.SUCCESS.value


async def test_missing_payment_raises_error(monkeypatch):
    session_context, _ = make_session_context(None)

    monkeypatch.setattr(
        consumer,
        "async_session",
        lambda: session_context,
    )

    payment_id = uuid4()

    with pytest.raises(ValueError, match="not found"):
        await consumer.process_payment(make_message(payment_id))

async def test_webhook_creation_error_is_propagated_and_transaction_exits_with_error(
    monkeypatch,
):
    payment = SimpleNamespace(
        id=uuid4(),
        status=Status.PENDING,
        hook_url="https://example.com/webhook",
    )
    session_context, session = make_session_context(payment)

    monkeypatch.setattr(
        consumer,
        "async_session",
        lambda: session_context,
    )
    monkeypatch.setattr(
        consumer,
        "asyncio",
        SimpleNamespace(sleep=AsyncMock()),
    )
    monkeypatch.setattr(
        consumer,
        "random",
        SimpleNamespace(uniform=lambda *_: 2, random=lambda: 0.1),
    )

    session.add.side_effect = RuntimeError("Webhook insert failed")

    with pytest.raises(RuntimeError, match="Webhook insert failed"):
        await consumer.process_payment(make_message(payment.id))

    transaction_context = session.begin.return_value
    transaction_context.__aexit__.assert_awaited_once()

    exit_args = transaction_context.__aexit__.await_args.args
    assert exit_args[0] is RuntimeError
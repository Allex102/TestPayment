import decimal
from typing import Any

from sqlalchemy import Enum, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities import Base
from src.domain.value_objects.enum import Currency, Status


class Payment(Base):
    __tablename__ = "payments"

    payment_sum: Mapped[decimal.Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Сумма платежа"
    )
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, name="currency"),
        nullable=False,
        default=Currency.RUB,
        comment="Валюта платежа",
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Комментарий"
    )
    meta: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Метаданные"
    )
    status: Mapped[Status] = mapped_column(
        Enum(Status, name="status"),
        nullable=False,
        default=Status.PENDING,
        comment="Статус"
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    hook_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=True
    )


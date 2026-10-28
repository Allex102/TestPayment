from decimal import Decimal
from typing import Any

from pydantic import Field, HttpUrl
from pydantic.dataclasses import dataclass

from src.domain.value_objects.enum import Currency


@dataclass(slots=True)
class PaymentCreateRequestDTO:
    payment_sum: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: Currency = Currency.RUB
    description: str | None = Field(default=None, max_length=255)
    meta: dict[str, Any] = Field(default_factory=dict)
    hook_url: HttpUrl | None = None

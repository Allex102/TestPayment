import decimal
from typing import Any

from pydantic import BaseModel, field_validator

from src.presentation.schemas.payment.validators import validate_currency, validate_hook_url, validate_sum

class PaymentCreateRequest(BaseModel):
    payment_sum: decimal.Decimal
    currency: str
    description: str
    meta: dict[str, Any]
    hook_url: str

    @field_validator("currency", mode="before")
    @classmethod
    def check_currency(cls, value: Any) -> str:
        return validate_currency(value).value

    @field_validator("hook_url")
    @classmethod
    def check_hook_url(cls, value: str | None) -> str:
        return validate_hook_url(value)

    @field_validator("payment_sum")
    @classmethod
    def check_payment_sum(cls, value: decimal.Decimal | None) -> decimal.Decimal:
        return validate_sum(value)
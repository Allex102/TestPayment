import decimal
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.value_objects.enum import Currency, Status


class PaymentCreateResponseDTO(BaseModel):
    payment_id: UUID
    status: Status
    created_at: datetime


class PaymentGetResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: UUID
    payment_sum: decimal.Decimal
    currency: Currency
    description: str
    meta: dict[str, Any]
    status: Status
    hook_url: str
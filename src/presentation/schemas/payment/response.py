import datetime
import decimal
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict


class PaymentCreateResponse(BaseModel):
    payment_id: uuid.UUID
    status: str
    created_at: datetime.datetime


class PaymentGetResponse(BaseModel):
    payment_id: uuid.UUID
    payment_sum: decimal.Decimal
    currency: str
    description: str
    meta: dict[str, Any]
    status: str
    hook_url: str

    model_config = ConfigDict(from_attributes=True)


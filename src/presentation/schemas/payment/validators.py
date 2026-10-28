import decimal
from typing import Any

from pydantic import HttpUrl

from src.domain.value_objects.enum import Currency
from src.presentation.exceptions import InvalidCurrencyException, InvalidUrlException


def validate_currency(value: Any) -> Currency:
    try:
        return Currency(value)
    except (ValueError, TypeError):
        allowed = ", ".join(currency.value for currency in Currency)
        raise InvalidCurrencyException(
            f"Недопустимая валюта: {value}. "
            f"Допустимые значения: {allowed}"
        )


def validate_hook_url(value: str | None) -> str | None:
    if value is None:
        return None

    try:
        return str(HttpUrl(value))
    except ValueError:
        raise InvalidUrlException(
            "hook_url должен быть корректным HTTP(S) URL"
        )

def validate_sum(value: decimal.Decimal) -> decimal.Decimal:
    if value <= 0:
        raise InvalidUrlException("Сумма платежа пуста или отрицательна")
    return decimal.Decimal(value)
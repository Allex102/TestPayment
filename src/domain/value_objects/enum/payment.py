from enum import StrEnum


class Currency(StrEnum):
    USD = "USD"
    RUB = "RUB"
    EUR = "EUR"


class Status(StrEnum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
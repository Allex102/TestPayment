from starlette import status

from src.domain.exceptions import CoreException


class InvalidCurrencyException(CoreException):
    code: str = "INVALID_CURRENCY"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class InvalidUrlException(CoreException):
    code: str = "INVALID_URL"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class InvalidPaymentSum(CoreException):
    code: str = "INVALID_PAYMENT_SUM"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
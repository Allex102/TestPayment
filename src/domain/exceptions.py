class CoreException(Exception):
    code: str = "error"
    status_code: int = 500

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PaymentNotExistException(CoreException):
    code: str = "PaymentNotExist"
    status_code: int = 404


class PaymentAlreadyExistException(CoreException):
    code: str = "PaymentAlreadyExist"
    status_code: int = 409

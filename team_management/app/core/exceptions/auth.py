from app.core.exceptions.base import AppException


class PasswordsDontMatchError(AppException):
    pass


class ForbiddenError(AppException):
    pass


class InvalidTokenTypeError(AppException):
    pass

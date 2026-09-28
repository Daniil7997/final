from app.core.exceptions.base import AppException


class UserNotFoundError(AppException):
    pass


class EmailAlreadyExistsError(AppException):
    pass

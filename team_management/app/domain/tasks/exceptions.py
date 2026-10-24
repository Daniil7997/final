from app.core.exceptions.base import AppException


class TaskNotFoundError(AppException):
    pass


class TaskNotDoneError(AppException):
    pass

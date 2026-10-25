from app.core.exceptions.base import AppException


class InviteStorageUnavailableError(AppException):
    pass


class InviteStorageNotConnectedError(AppException):
    pass


class TokensBlacklistUnavailableError(AppException):
    pass

from app.core.exceptions.base import AppException


class MeetingsOverlapError(AppException):
    pass


class InvalidMeetingTimeRangeError(AppException):
    pass


class MeetingNotFoundError(AppException):
    pass


class UserAlreadyInMeetingError(AppException):
    pass


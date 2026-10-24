from app.core.exceptions.base import AppException


class TeamNameAlreadyExistError(AppException):
    pass


class TeamNotFoundError(AppException):
    pass


class InviteNotFoundError(AppException):
    pass


class TeamMembershipRequiredError(AppException):
    pass


class TeamMemberNotFoundError(AppException):
    pass


class LowActorRolePrivilegeError(AppException):
    pass

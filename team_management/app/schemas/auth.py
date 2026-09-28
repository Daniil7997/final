from pydantic import BaseModel

from app.schemas.types import (UserNameType,
                               PasswordType,
                               EmailType,
                               UserRoleType,
                               IdType)


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class RegisterUserRequest(BaseModel):
    name: UserNameType
    password: PasswordType
    email: EmailType


class RegisterUserResponse(BaseModel):
    id: IdType
    name: UserNameType
    email: EmailType


class TokensRequest(BaseModel):
    password: PasswordType
    email: EmailType


class TokensResponse(BaseModel):
    access: str
    refresh: str


class ChangePasswordRequest(BaseModel):
    old_password: PasswordType
    new_password: PasswordType


# ======================================================
# INTERNAL AUTH STRUCTURES (JWT / SECURITY LAYER)
# ======================================================
class AccessTokensPayload(BaseModel):
    sub: IdType
    iat: int
    exp: int
    user_role: UserRoleType
    token_type: str


class RefreshTokensPayload(BaseModel):
    sub: IdType
    iat: int
    exp: int
    token_type: str


class Tokens(BaseModel):
    access: str
    refresh: str

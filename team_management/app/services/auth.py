from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError

from app.core.exceptions.auth import PasswordsDontMatchError
from app.core.infrastructure.tokens_blacklist.blacklist import tokens_blacklist
from app.core.security import create_tokens, hash_password, verify_password
from app.domain.users.exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
)
from app.schemas.auth import (
    AccessTokensPayload,
    ChangePasswordRequest,
    RegisterUserRequest,
    RegisterUserResponse,
    TokensRequest,
    TokensResponse,
)
from app.schemas.structural import UsersSchema
from app.schemas.types import IdType
from app.services.base import BaseService


class AuthService(BaseService):

    async def register_user(self,
                            data: RegisterUserRequest) -> RegisterUserResponse:
        hashed_password = hash_password(password=data.password)
        async with self.unit_of_work as uow:
            repo = uow.users
            try:
                user: UsersSchema = await repo.register_user(
                    name=data.name,
                    email=data.email,
                    hashed_password=hashed_password
                    )
                return RegisterUserResponse.model_validate(user.model_dump())
            except IntegrityError:
                raise EmailAlreadyExistsError()

    async def get_tokens(self, data: TokensRequest) -> TokensResponse:
        async with self.unit_of_work as uow:
            repo = uow.users
            user: UsersSchema | None = await repo.get_user_by_email(
                email=data.email
                )
            if user is None:
                raise UserNotFoundError()
            check_password = verify_password(raw_password=data.password,
                                             hash_password=user.password)
            if not check_password:
                raise PasswordsDontMatchError()
            tokens = create_tokens(user_id=user.id)
            return TokensResponse.model_validate(tokens.model_dump())

    async def change_password(self,
                              data: ChangePasswordRequest,
                              id: IdType):
        async with self.unit_of_work as uow:
            repo = uow.users
            user: UsersSchema | None = await repo.get_user_by_id(id=id)
            if user is None:
                raise UserNotFoundError()
            passwords_match = verify_password(hash_password=user.password,
                                              raw_password=data.old_password)
            if not passwords_match:
                raise PasswordsDontMatchError()
            new_password = hash_password(data.new_password)
            await repo.update_user_data_by_id(
                id=id,
                update_data={'password': new_password}
                )

    async def logout(self, token: str, payload: AccessTokensPayload) -> None:
        current_time = datetime.now(UTC).timestamp()
        expire = int(payload.exp - current_time)
        await tokens_blacklist.set(key=token,
                                   value=str(payload.sub),
                                   expire=expire)

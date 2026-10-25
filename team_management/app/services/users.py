from app.domain.users.exceptions import UserNotFoundError
from app.schemas.structural import UsersSchema
from app.schemas.types import IdType
from app.schemas.users import GetProfileResponse
from app.services.base import BaseService


class UsersService(BaseService):

    async def profile_by_id(self, id: IdType):
        async with self.unit_of_work as uow:
            repo = uow.users
            user: UsersSchema | None = await repo.get_user_by_id(id=id)
            if user is None:
                raise UserNotFoundError()
            return GetProfileResponse.model_validate(user.model_dump())

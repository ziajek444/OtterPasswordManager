from collections.abc import Callable

from otter_password_manager.application.exceptions import (
    LoginAlreadyExistsError,
    PasswordTooShortError,
    UserNotFoundError,
)
from otter_password_manager.application.ports.password_hasher import PasswordHasher
from otter_password_manager.application.ports.unit_of_work import UnitOfWork
from otter_password_manager.domain.entities.user import User


class UserService:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        password_hasher: PasswordHasher,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._password_hasher = password_hasher

    async def create(self, *, login: str, password: str) -> User:
        if len(password) < 12:
            raise PasswordTooShortError(12)
        async with self._unit_of_work_factory() as unit_of_work:
            if await unit_of_work.users.get_by_login(login) is not None:
                raise LoginAlreadyExistsError(login)
            user = await unit_of_work.users.add(login, self._password_hasher.hash(password))
            await unit_of_work.commit()
            return user

    async def get(self, user_id: int) -> User:
        async with self._unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(user_id)
            return user

    async def list(self, *, offset: int, limit: int) -> list[User]:
        async with self._unit_of_work_factory() as unit_of_work:
            return await unit_of_work.users.list(offset=offset, limit=limit)

    async def update(
        self, user_id: int, *, login: str | None, password: str | None
    ) -> User:
        async with self._unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(user_id)
            if login is not None:
                existing = await unit_of_work.users.get_by_login(login)
                if existing is not None and existing.id != user_id:
                    raise LoginAlreadyExistsError(login)
            hashed_password = self._password_hasher.hash(password) if password else None
            updated = await unit_of_work.users.update(
                user, login=login, hashed_password=hashed_password
            )
            await unit_of_work.commit()
            return updated

    async def delete(self, user_id: int) -> None:
        async with self._unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(user_id)
            await unit_of_work.users.delete(user)
            await unit_of_work.commit()

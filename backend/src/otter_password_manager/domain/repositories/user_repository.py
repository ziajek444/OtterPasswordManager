from abc import ABC, abstractmethod

from otter_password_manager.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def add(self, login: str, hashed_password: str) -> User: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_login(self, login: str) -> User | None: ...

    @abstractmethod
    async def list(self, *, offset: int, limit: int) -> list[User]: ...

    @abstractmethod
    async def update(
        self, user: User, *, login: str | None, hashed_password: str | None
    ) -> User: ...

    @abstractmethod
    async def delete(self, user: User) -> None: ...


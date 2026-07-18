from abc import ABC, abstractmethod
from types import TracebackType

from otter_password_manager.domain.repositories.password_entry_repository import (
    PasswordEntryRepository,
)
from otter_password_manager.domain.repositories.user_repository import UserRepository


class UnitOfWork(ABC):
    users: UserRepository
    password_entries: PasswordEntryRepository

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork": ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from otter_password_manager.application.ports.unit_of_work import UnitOfWork
from otter_password_manager.infrastructure.database.repositories.password_entry_repository import (
    SqlAlchemyPasswordEntryRepository,
)
from otter_password_manager.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self._session)
        self.password_entries = SqlAlchemyPasswordEntryRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self._session.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

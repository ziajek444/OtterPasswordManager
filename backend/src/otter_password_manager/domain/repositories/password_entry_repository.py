from abc import ABC, abstractmethod

from otter_password_manager.domain.entities.password_entry import PasswordEntry


class PasswordEntryRepository(ABC):
    @abstractmethod
    async def add(
        self,
        *,
        owner_id: int,
        service_name: str,
        username: str,
        encrypted_password: str,
        website: str | None,
        notes: str | None,
    ) -> PasswordEntry: ...

    @abstractmethod
    async def get_owned(self, entry_id: int, owner_id: int) -> PasswordEntry | None: ...

    @abstractmethod
    async def list_owned(self, owner_id: int) -> list[PasswordEntry]: ...

    @abstractmethod
    async def update(
        self,
        entry: PasswordEntry,
        *,
        service_name: str,
        username: str,
        encrypted_password: str,
        website: str | None,
        notes: str | None,
    ) -> PasswordEntry: ...

    @abstractmethod
    async def delete(self, entry: PasswordEntry) -> None: ...

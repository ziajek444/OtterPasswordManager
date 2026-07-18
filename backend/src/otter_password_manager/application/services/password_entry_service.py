from collections.abc import Callable

from otter_password_manager.application.dto.password_entries import PasswordEntryDetails
from otter_password_manager.application.exceptions import PasswordEntryNotFoundError
from otter_password_manager.application.ports.encryption import EncryptionPort
from otter_password_manager.application.ports.unit_of_work import UnitOfWork
from otter_password_manager.domain.entities.password_entry import PasswordEntry


class PasswordEntryService:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        encryption: EncryptionPort,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._encryption = encryption

    async def create(
        self,
        *,
        owner_id: int,
        service_name: str,
        username: str,
        password: str,
        website: str | None,
        notes: str | None,
    ) -> PasswordEntryDetails:
        async with self._unit_of_work_factory() as unit_of_work:
            entry = await unit_of_work.password_entries.add(
                owner_id=owner_id,
                service_name=service_name,
                username=username,
                encrypted_password=self._encryption.encrypt(password),
                website=website,
                notes=notes,
            )
            await unit_of_work.commit()
            return self._details(entry)

    async def get(self, *, entry_id: int, owner_id: int) -> PasswordEntryDetails:
        async with self._unit_of_work_factory() as unit_of_work:
            entry = await unit_of_work.password_entries.get_owned(entry_id, owner_id)
            if entry is None:
                raise PasswordEntryNotFoundError(entry_id)
            return self._details(entry)

    async def list(self, *, owner_id: int) -> list[PasswordEntryDetails]:
        async with self._unit_of_work_factory() as unit_of_work:
            entries = await unit_of_work.password_entries.list_owned(owner_id)
            return [self._details(entry) for entry in entries]

    async def update(
        self,
        *,
        entry_id: int,
        owner_id: int,
        service_name: str,
        username: str,
        password: str,
        website: str | None,
        notes: str | None,
    ) -> PasswordEntryDetails:
        async with self._unit_of_work_factory() as unit_of_work:
            entry = await unit_of_work.password_entries.get_owned(entry_id, owner_id)
            if entry is None:
                raise PasswordEntryNotFoundError(entry_id)
            updated = await unit_of_work.password_entries.update(
                entry,
                service_name=service_name,
                username=username,
                encrypted_password=self._encryption.encrypt(password),
                website=website,
                notes=notes,
            )
            await unit_of_work.commit()
            return self._details(updated)

    async def delete(self, *, entry_id: int, owner_id: int) -> None:
        async with self._unit_of_work_factory() as unit_of_work:
            entry = await unit_of_work.password_entries.get_owned(entry_id, owner_id)
            if entry is None:
                raise PasswordEntryNotFoundError(entry_id)
            await unit_of_work.password_entries.delete(entry)
            await unit_of_work.commit()

    def _details(self, entry: PasswordEntry) -> PasswordEntryDetails:
        return PasswordEntryDetails(
            id=entry.id,
            service_name=entry.service_name,
            username=entry.username,
            password=self._encryption.decrypt(entry.encrypted_password),
            website=entry.website,
            notes=entry.notes,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )

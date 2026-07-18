from datetime import UTC, datetime

import pytest

from otter_password_manager.application.exceptions import PasswordEntryNotFoundError
from otter_password_manager.application.ports.encryption import EncryptionPort
from otter_password_manager.application.ports.unit_of_work import UnitOfWork
from otter_password_manager.application.services.password_entry_service import PasswordEntryService
from otter_password_manager.domain.entities.password_entry import PasswordEntry
from otter_password_manager.domain.repositories.password_entry_repository import (
    PasswordEntryRepository,
)


class FakeEncryption(EncryptionPort):
    def encrypt(self, plaintext: str) -> str:
        return f"encrypted:{plaintext}"

    def decrypt(self, encrypted_value: str) -> str:
        return encrypted_value.removeprefix("encrypted:")


class FakePasswordEntryRepository(PasswordEntryRepository):
    def __init__(self, entries: list[PasswordEntry] | None = None) -> None:
        self.entries = entries or []

    async def add(
        self,
        *,
        owner_id: int,
        service_name: str,
        username: str,
        encrypted_password: str,
        website: str | None,
        notes: str | None,
    ) -> PasswordEntry:
        now = datetime.now(UTC)
        entry = PasswordEntry(
            len(self.entries) + 1,
            owner_id,
            service_name,
            username,
            encrypted_password,
            website,
            notes,
            now,
            now,
        )
        self.entries.append(entry)
        return entry

    async def get_owned(self, entry_id: int, owner_id: int) -> PasswordEntry | None:
        return next(
            (
                entry
                for entry in self.entries
                if entry.id == entry_id and entry.owner_id == owner_id
            ),
            None,
        )

    async def list_owned(self, owner_id: int) -> list[PasswordEntry]:
        return [entry for entry in self.entries if entry.owner_id == owner_id]

    async def update(
        self,
        entry: PasswordEntry,
        *,
        service_name: str,
        username: str,
        encrypted_password: str,
        website: str | None,
        notes: str | None,
    ) -> PasswordEntry:
        updated = PasswordEntry(
            entry.id,
            entry.owner_id,
            service_name,
            username,
            encrypted_password,
            website,
            notes,
            entry.created_at,
            datetime.now(UTC),
        )
        self.entries[self.entries.index(entry)] = updated
        return updated

    async def delete(self, entry: PasswordEntry) -> None:
        self.entries.remove(entry)


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, entries: FakePasswordEntryRepository) -> None:
        self.password_entries = entries
        self.committed = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass

    async def commit(self) -> None:
        self.committed = True


def build_service(
    repository: FakePasswordEntryRepository,
) -> tuple[PasswordEntryService, FakeUnitOfWork]:
    unit_of_work = FakeUnitOfWork(repository)
    return PasswordEntryService(lambda: unit_of_work, FakeEncryption()), unit_of_work


@pytest.mark.asyncio
async def test_create_encrypts_password_and_returns_plaintext_to_owner() -> None:
    repository = FakePasswordEntryRepository()
    service, unit_of_work = build_service(repository)

    result = await service.create(
        owner_id=7,
        service_name="Example",
        username="otter",
        password="secret",
        website=None,
        notes=None,
    )

    assert repository.entries[0].encrypted_password == "encrypted:secret"
    assert result.password == "secret"
    assert unit_of_work.committed is True


@pytest.mark.asyncio
async def test_get_does_not_return_entry_owned_by_another_user() -> None:
    now = datetime.now(UTC)
    entry = PasswordEntry(1, 7, "Example", "otter", "encrypted:secret", None, None, now, now)
    service, _ = build_service(FakePasswordEntryRepository([entry]))

    with pytest.raises(PasswordEntryNotFoundError):
        await service.get(entry_id=1, owner_id=8)


@pytest.mark.asyncio
async def test_list_returns_only_owner_entries() -> None:
    now = datetime.now(UTC)
    entries = [
        PasswordEntry(1, 7, "One", "a", "encrypted:one", None, None, now, now),
        PasswordEntry(2, 8, "Two", "b", "encrypted:two", None, None, now, now),
    ]
    service, _ = build_service(FakePasswordEntryRepository(entries))

    result = await service.list(owner_id=7)

    assert [entry.id for entry in result] == [1]


@pytest.mark.asyncio
async def test_update_and_delete_require_owner() -> None:
    now = datetime.now(UTC)
    entry = PasswordEntry(1, 7, "Old", "old", "encrypted:old", None, None, now, now)
    repository = FakePasswordEntryRepository([entry])
    service, unit_of_work = build_service(repository)

    updated = await service.update(
        entry_id=1,
        owner_id=7,
        service_name="New",
        username="new",
        password="new-secret",
        website="https://example.com",
        notes="note",
    )
    await service.delete(entry_id=1, owner_id=7)

    assert updated.password == "new-secret"
    assert repository.entries == []
    assert unit_of_work.committed is True

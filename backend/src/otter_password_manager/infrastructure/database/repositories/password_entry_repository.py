from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from otter_password_manager.domain.entities.password_entry import PasswordEntry
from otter_password_manager.domain.repositories.password_entry_repository import (
    PasswordEntryRepository,
)
from otter_password_manager.infrastructure.database.models.password_entry_model import (
    PasswordEntryModel,
)


def _to_domain(model: PasswordEntryModel) -> PasswordEntry:
    return PasswordEntry(
        id=model.id,
        owner_id=model.owner_id,
        service_name=model.service_name,
        username=model.username,
        encrypted_password=model.encrypted_password,
        website=model.website,
        notes=model.notes,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyPasswordEntryRepository(PasswordEntryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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
        model = PasswordEntryModel(
            owner_id=owner_id,
            service_name=service_name,
            username=username,
            encrypted_password=encrypted_password,
            website=website,
            notes=notes,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_domain(model)

    async def get_owned(self, entry_id: int, owner_id: int) -> PasswordEntry | None:
        model = await self._session.scalar(
            select(PasswordEntryModel).where(
                PasswordEntryModel.id == entry_id,
                PasswordEntryModel.owner_id == owner_id,
            )
        )
        return _to_domain(model) if model else None

    async def list_owned(self, owner_id: int) -> list[PasswordEntry]:
        result = await self._session.scalars(
            select(PasswordEntryModel)
            .where(PasswordEntryModel.owner_id == owner_id)
            .order_by(PasswordEntryModel.service_name, PasswordEntryModel.id)
        )
        return [_to_domain(model) for model in result]

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
        model = await self._session.scalar(
            select(PasswordEntryModel).where(
                PasswordEntryModel.id == entry.id,
                PasswordEntryModel.owner_id == entry.owner_id,
            )
        )
        if model is None:
            raise RuntimeError("Password entry disappeared during the transaction")
        model.service_name = service_name
        model.username = username
        model.encrypted_password = encrypted_password
        model.website = website
        model.notes = notes
        await self._session.flush()
        await self._session.refresh(model)
        return _to_domain(model)

    async def delete(self, entry: PasswordEntry) -> None:
        model = await self._session.scalar(
            select(PasswordEntryModel).where(
                PasswordEntryModel.id == entry.id,
                PasswordEntryModel.owner_id == entry.owner_id,
            )
        )
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()

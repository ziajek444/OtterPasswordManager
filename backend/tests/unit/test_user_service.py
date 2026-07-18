from datetime import UTC, datetime

import pytest

from otter_password_manager.application.exceptions import (
    LoginAlreadyExistsError,
    PasswordTooShortError,
)
from otter_password_manager.application.ports.password_hasher import PasswordHasher
from otter_password_manager.application.ports.unit_of_work import UnitOfWork
from otter_password_manager.application.services.user_service import UserService
from otter_password_manager.domain.entities.user import User
from otter_password_manager.domain.repositories.user_repository import UserRepository


class FakePasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, encoded_hash: str) -> bool:
        return encoded_hash == self.hash(password)


class FakeUserRepository(UserRepository):
    def __init__(self, users: list[User] | None = None) -> None:
        self.users = users or []

    async def add(self, login: str, hashed_password: str) -> User:
        user = User(len(self.users) + 1, login, hashed_password, datetime.now(UTC))
        self.users.append(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        return next((user for user in self.users if user.id == user_id), None)

    async def get_by_login(self, login: str) -> User | None:
        return next((user for user in self.users if user.login == login), None)

    async def list(self, *, offset: int, limit: int) -> list[User]:
        return self.users[offset : offset + limit]

    async def update(
        self, user: User, *, login: str | None, hashed_password: str | None
    ) -> User:
        raise NotImplementedError

    async def delete(self, user: User) -> None:
        raise NotImplementedError


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, users: FakeUserRepository) -> None:
        self.users = users
        self.committed = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass

    async def commit(self) -> None:
        self.committed = True


@pytest.mark.asyncio
async def test_create_user_hashes_password_and_commits() -> None:
    repository = FakeUserRepository()
    unit_of_work = FakeUnitOfWork(repository)
    service = UserService(lambda: unit_of_work, FakePasswordHasher())

    user = await service.create(login="otter", password="secure-pass-12")

    assert user.login == "otter"
    assert user.hashed_password == "hashed:secure-pass-12"
    assert unit_of_work.committed is True


@pytest.mark.asyncio
async def test_create_user_rejects_duplicate_login() -> None:
    existing = User(1, "otter", "hash", datetime.now(UTC))
    service = UserService(
        lambda: FakeUnitOfWork(FakeUserRepository([existing])), FakePasswordHasher()
    )

    with pytest.raises(LoginAlreadyExistsError):
        await service.create(login="otter", password="secure-pass-12")


@pytest.mark.asyncio
async def test_create_user_rejects_password_shorter_than_twelve_characters() -> None:
    service = UserService(
        lambda: FakeUnitOfWork(FakeUserRepository()), FakePasswordHasher()
    )

    with pytest.raises(PasswordTooShortError):
        await service.create(login="otter", password="short")


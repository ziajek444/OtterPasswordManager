from datetime import UTC, datetime

import pytest

from otter_password_manager.application.dto.tokens import AccessTokenPayload, TokenPair
from otter_password_manager.application.exceptions import InvalidCredentialsError
from otter_password_manager.application.ports.token_service import TokenService
from otter_password_manager.application.services.authentication_service import (
    AuthenticationService,
)
from otter_password_manager.domain.entities.user import User
from tests.unit.test_user_service import (
    FakePasswordHasher,
    FakeUnitOfWork,
    FakeUserRepository,
)


class FakeTokenService(TokenService):
    def create_pair(self, user: User) -> TokenPair:
        return TokenPair("access-token", "refresh-token")

    def decode_access_token(self, token: str) -> AccessTokenPayload:
        return AccessTokenPayload(1, "otter")


def build_service(users: list[User]) -> AuthenticationService:
    return AuthenticationService(
        lambda: FakeUnitOfWork(FakeUserRepository(users)),
        FakePasswordHasher(),
        FakeTokenService(),
    )


@pytest.mark.asyncio
async def test_login_returns_access_and_refresh_tokens() -> None:
    user = User(1, "otter", "hashed:secure-pass-12", datetime.now(UTC))

    tokens = await build_service([user]).login(login="otter", password="secure-pass-12")

    assert tokens == TokenPair("access-token", "refresh-token")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("login", "password"),
    [("unknown", "secure-pass-12"), ("otter", "wrong-password")],
)
async def test_login_rejects_invalid_credentials(login: str, password: str) -> None:
    user = User(1, "otter", "hashed:secure-pass-12", datetime.now(UTC))

    with pytest.raises(InvalidCredentialsError):
        await build_service([user]).login(login=login, password=password)

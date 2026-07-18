from datetime import UTC, datetime

import pytest

from otter_password_manager.application.ports.token_service import InvalidTokenError
from otter_password_manager.domain.entities.user import User
from otter_password_manager.infrastructure.security.jwt_token_service import JwtTokenService


def test_access_token_can_be_decoded_and_refresh_token_cannot() -> None:
    service = JwtTokenService(
        secret="a-test-secret-that-is-at-least-32-characters",
        access_token_minutes=15,
        refresh_token_days=30,
    )
    user = User(7, "otter", "hash", datetime.now(UTC))

    tokens = service.create_pair(user)
    payload = service.decode_access_token(tokens.access_token)

    assert payload.user_id == 7
    assert payload.login == "otter"
    with pytest.raises(InvalidTokenError):
        service.decode_access_token(tokens.refresh_token)

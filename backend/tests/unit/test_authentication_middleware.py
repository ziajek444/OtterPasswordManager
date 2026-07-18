from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from otter_password_manager.application.dto.tokens import AccessTokenPayload
from otter_password_manager.application.ports.token_service import InvalidTokenError
from otter_password_manager.presentation.middleware import jwt_authentication_middleware


class FakeTokenService:
    def decode_access_token(self, token: str) -> AccessTokenPayload:
        if token != "valid-access-token":
            raise InvalidTokenError
        return AccessTokenPayload(user_id=1, login="otter")


def create_test_app() -> FastAPI:
    app = FastAPI()
    app.state.container = SimpleNamespace(token_service=FakeTokenService())
    app.middleware("http")(jwt_authentication_middleware)

    @app.get("/api/v1/protected")
    async def protected() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/passwords")
    async def passwords() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/login")
    async def public() -> dict[str, str]:
        return {"status": "public"}

    return app


def test_middleware_rejects_missing_token() -> None:
    response = TestClient(create_test_app()).get("/passwords")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_middleware_rejects_invalid_token() -> None:
    response = TestClient(create_test_app()).get(
        "/api/v1/protected", headers={"Authorization": "Bearer invalid"}
    )

    assert response.status_code == 401


def test_middleware_accepts_valid_access_token() -> None:
    response = TestClient(create_test_app()).get(
        "/api/v1/protected", headers={"Authorization": "Bearer valid-access-token"}
    )

    assert response.status_code == 200


def test_middleware_allows_public_route() -> None:
    response = TestClient(create_test_app()).get("/login")

    assert response.status_code == 200

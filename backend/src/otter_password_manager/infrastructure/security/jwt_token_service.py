from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from otter_password_manager.application.dto.tokens import AccessTokenPayload, TokenPair
from otter_password_manager.application.ports.token_service import InvalidTokenError, TokenService
from otter_password_manager.domain.entities.user import User


class JwtTokenService(TokenService):
    _ALGORITHM = "HS256"

    def __init__(
        self, *, secret: str, access_token_minutes: int, refresh_token_days: int
    ) -> None:
        self._secret = secret
        self._access_token_lifetime = timedelta(minutes=access_token_minutes)
        self._refresh_token_lifetime = timedelta(days=refresh_token_days)

    def create_pair(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=self._encode(user, "access", self._access_token_lifetime),
            refresh_token=self._encode(user, "refresh", self._refresh_token_lifetime),
        )

    def decode_access_token(self, token: str) -> AccessTokenPayload:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._ALGORITHM])
            if payload.get("type") != "access":
                raise InvalidTokenError
            return AccessTokenPayload(user_id=int(payload["sub"]), login=payload["login"])
        except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
            raise InvalidTokenError from exc

    def _encode(self, user: User, token_type: str, lifetime: timedelta) -> str:
        now = datetime.now(UTC)
        return jwt.encode(
            {
                "sub": str(user.id),
                "login": user.login,
                "type": token_type,
                "iat": now,
                "exp": now + lifetime,
                "jti": str(uuid4()),
            },
            self._secret,
            algorithm=self._ALGORITHM,
        )

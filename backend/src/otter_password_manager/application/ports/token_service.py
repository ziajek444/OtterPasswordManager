from abc import ABC, abstractmethod

from otter_password_manager.application.dto.tokens import AccessTokenPayload, TokenPair
from otter_password_manager.domain.entities.user import User


class InvalidTokenError(Exception):
    pass


class TokenService(ABC):
    @abstractmethod
    def create_pair(self, user: User) -> TokenPair: ...

    @abstractmethod
    def decode_access_token(self, token: str) -> AccessTokenPayload: ...

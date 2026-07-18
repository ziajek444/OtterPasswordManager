from argon2 import PasswordHasher as Argon2LibraryHasher
from argon2.exceptions import InvalidHashError, VerificationError

from otter_password_manager.application.ports.password_hasher import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._hasher = Argon2LibraryHasher()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password: str, encoded_hash: str) -> bool:
        try:
            return self._hasher.verify(encoded_hash, password)
        except (InvalidHashError, VerificationError):
            return False


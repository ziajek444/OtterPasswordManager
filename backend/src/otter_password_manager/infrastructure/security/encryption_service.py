import base64
import binascii
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from otter_password_manager.application.ports.encryption import EncryptionPort


class EncryptionError(Exception):
    """Raised when encrypted data is malformed or fails authentication."""


class EncryptionConfigurationError(Exception):
    """Raised when the configured encryption key is invalid."""


class EncryptionService(EncryptionPort):
    _VERSION = "v1"
    _NONCE_LENGTH = 12
    _ASSOCIATED_DATA = b"otter-password-manager:password-entry:v1"

    def __init__(self, encoded_key: str) -> None:
        try:
            key = base64.b64decode(encoded_key, altchars=b"-_", validate=True)
        except (ValueError, binascii.Error) as exc:
            raise EncryptionConfigurationError(
                "Encryption key must be valid URL-safe Base64"
            ) from exc
        if len(key) != 32:
            raise EncryptionConfigurationError("AES-256-GCM requires a 32-byte key")
        self._cipher = AESGCM(key)

    def encrypt(self, plaintext: str) -> str:
        nonce = secrets.token_bytes(self._NONCE_LENGTH)
        ciphertext = self._cipher.encrypt(
            nonce, plaintext.encode("utf-8"), self._ASSOCIATED_DATA
        )
        return ".".join(
            (
                self._VERSION,
                self._encode(nonce),
                self._encode(ciphertext),
            )
        )

    def decrypt(self, encrypted_value: str) -> str:
        try:
            version, encoded_nonce, encoded_ciphertext = encrypted_value.split(".")
            if version != self._VERSION:
                raise EncryptionError("Unsupported encrypted value version")
            nonce = self._decode(encoded_nonce)
            if len(nonce) != self._NONCE_LENGTH:
                raise EncryptionError("Invalid nonce length")
            ciphertext = self._decode(encoded_ciphertext)
            plaintext = self._cipher.decrypt(nonce, ciphertext, self._ASSOCIATED_DATA)
            return plaintext.decode("utf-8")
        except EncryptionError:
            raise
        except (ValueError, binascii.Error, InvalidTag, UnicodeDecodeError) as exc:
            raise EncryptionError("Encrypted value is invalid or has been modified") from exc

    @staticmethod
    def _encode(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")

    @staticmethod
    def _decode(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.b64decode(value + padding, altchars=b"-_", validate=True)

import base64

import pytest

from otter_password_manager.infrastructure.security.encryption_service import (
    EncryptionConfigurationError,
    EncryptionError,
    EncryptionService,
)

KEY = base64.urlsafe_b64encode(bytes(range(32))).decode("ascii")


def test_encrypt_and_decrypt_password() -> None:
    service = EncryptionService(KEY)
    plaintext = "correct horse battery staple 🔐"

    encrypted = service.encrypt(plaintext)

    assert plaintext not in encrypted
    assert encrypted.startswith("v1.")
    assert service.decrypt(encrypted) == plaintext


def test_encryption_uses_a_fresh_nonce() -> None:
    service = EncryptionService(KEY)

    first = service.encrypt("same password")
    second = service.encrypt("same password")

    assert first != second


def test_decrypt_rejects_modified_ciphertext() -> None:
    service = EncryptionService(KEY)
    encrypted = service.encrypt("secret")
    version, nonce, ciphertext = encrypted.split(".")
    replacement = "A" if ciphertext[0] != "A" else "B"
    modified = ".".join((version, nonce, replacement + ciphertext[1:]))

    with pytest.raises(EncryptionError):
        service.decrypt(modified)


def test_configuration_rejects_non_256_bit_key() -> None:
    short_key = base64.urlsafe_b64encode(b"too short").decode("ascii")

    with pytest.raises(EncryptionConfigurationError):
        EncryptionService(short_key)

from otter_password_manager.infrastructure.security import Argon2PasswordHasher


def test_argon2_hash_does_not_contain_plain_password() -> None:
    hasher = Argon2PasswordHasher()
    password = "secure-pass-12"

    encoded_hash = hasher.hash(password)

    assert password not in encoded_hash
    assert encoded_hash.startswith("$argon2")
    assert hasher.verify(password, encoded_hash) is True
    assert hasher.verify("wrong-password", encoded_hash) is False


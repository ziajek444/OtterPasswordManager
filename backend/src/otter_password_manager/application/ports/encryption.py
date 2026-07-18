from abc import ABC, abstractmethod


class EncryptionPort(ABC):
    @abstractmethod
    def encrypt(self, plaintext: str) -> str: ...

    @abstractmethod
    def decrypt(self, encrypted_value: str) -> str: ...

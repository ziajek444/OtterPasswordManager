from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PasswordEntry:
    id: int
    owner_id: int
    service_name: str
    username: str
    encrypted_password: str
    website: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


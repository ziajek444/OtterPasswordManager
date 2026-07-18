from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PasswordEntryDetails:
    id: int
    service_name: str
    username: str
    password: str
    website: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

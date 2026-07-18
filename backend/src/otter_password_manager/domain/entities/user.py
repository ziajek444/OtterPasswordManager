from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class User:
    id: int
    login: str
    hashed_password: str
    created_at: datetime


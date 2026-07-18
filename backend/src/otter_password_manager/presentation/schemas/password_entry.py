from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PasswordEntryWrite(BaseModel):
    service_name: str = Field(min_length=1, max_length=200)
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=4096)
    website: str | None = Field(default=None, max_length=2048)
    notes: str | None = Field(default=None, max_length=10_000)


class PasswordEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_name: str
    username: str
    password: str
    website: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

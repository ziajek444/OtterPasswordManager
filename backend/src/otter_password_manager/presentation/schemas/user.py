from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    login: str = Field(min_length=3, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=128)


class UserUpdate(BaseModel):
    login: str | None = Field(
        default=None, min_length=3, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$"
    )
    password: str | None = Field(default=None, min_length=12, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    created_at: datetime


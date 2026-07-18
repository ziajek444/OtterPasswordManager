from typing import Annotated

from fastapi import APIRouter, Path, Response, status

from otter_password_manager.presentation.dependencies.authentication import (
    CurrentUserDependency,
)
from otter_password_manager.presentation.dependencies.services import (
    PasswordEntryServiceDependency,
)
from otter_password_manager.presentation.schemas.password_entry import (
    PasswordEntryResponse,
    PasswordEntryWrite,
)

router = APIRouter(prefix="/passwords", tags=["passwords"])
EntryId = Annotated[int, Path(gt=0)]


@router.get("", response_model=list[PasswordEntryResponse])
async def list_passwords(
    current_user: CurrentUserDependency,
    service: PasswordEntryServiceDependency,
) -> list[PasswordEntryResponse]:
    entries = await service.list(owner_id=current_user.user_id)
    return [PasswordEntryResponse.model_validate(entry) for entry in entries]


@router.get("/{entry_id}", response_model=PasswordEntryResponse)
async def get_password(
    entry_id: EntryId,
    current_user: CurrentUserDependency,
    service: PasswordEntryServiceDependency,
) -> PasswordEntryResponse:
    entry = await service.get(entry_id=entry_id, owner_id=current_user.user_id)
    return PasswordEntryResponse.model_validate(entry)


@router.post("", response_model=PasswordEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_password(
    payload: PasswordEntryWrite,
    current_user: CurrentUserDependency,
    service: PasswordEntryServiceDependency,
) -> PasswordEntryResponse:
    entry = await service.create(
        owner_id=current_user.user_id,
        service_name=payload.service_name,
        username=payload.username,
        password=payload.password,
        website=payload.website,
        notes=payload.notes,
    )
    return PasswordEntryResponse.model_validate(entry)


@router.put("/{entry_id}", response_model=PasswordEntryResponse)
async def update_password(
    entry_id: EntryId,
    payload: PasswordEntryWrite,
    current_user: CurrentUserDependency,
    service: PasswordEntryServiceDependency,
) -> PasswordEntryResponse:
    entry = await service.update(
        entry_id=entry_id,
        owner_id=current_user.user_id,
        service_name=payload.service_name,
        username=payload.username,
        password=payload.password,
        website=payload.website,
        notes=payload.notes,
    )
    return PasswordEntryResponse.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_password(
    entry_id: EntryId,
    current_user: CurrentUserDependency,
    service: PasswordEntryServiceDependency,
) -> Response:
    await service.delete(entry_id=entry_id, owner_id=current_user.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

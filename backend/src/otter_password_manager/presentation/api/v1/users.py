from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from otter_password_manager.presentation.dependencies.services import UserServiceDependency
from otter_password_manager.presentation.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, service: UserServiceDependency) -> UserResponse:
    return UserResponse.model_validate(
        await service.create(login=payload.login, password=payload.password)
    )


@router.get("", response_model=list[UserResponse])
async def list_users(
    service: UserServiceDependency,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[UserResponse]:
    users = await service.list(offset=offset, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, service: UserServiceDependency) -> UserResponse:
    return UserResponse.model_validate(await service.get(user_id))


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, payload: UserUpdate, service: UserServiceDependency
) -> UserResponse:
    return UserResponse.model_validate(
        await service.update(user_id, login=payload.login, password=payload.password)
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, service: UserServiceDependency) -> Response:
    await service.delete(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


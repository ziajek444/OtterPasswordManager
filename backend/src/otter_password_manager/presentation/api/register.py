from fastapi import APIRouter, status

from otter_password_manager.presentation.dependencies.services import UserServiceDependency
from otter_password_manager.presentation.schemas.user import UserCreate, UserResponse

router = APIRouter(tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, service: UserServiceDependency) -> UserResponse:
    user = await service.create(login=payload.login, password=payload.password)
    return UserResponse.model_validate(user)


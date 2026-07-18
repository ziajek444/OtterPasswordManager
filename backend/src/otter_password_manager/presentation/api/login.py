from fastapi import APIRouter

from otter_password_manager.presentation.dependencies.services import (
    AuthenticationServiceDependency,
)
from otter_password_manager.presentation.schemas.authentication import (
    LoginRequest,
    TokenPairResponse,
)

router = APIRouter(tags=["authentication"])


@router.post("/login", response_model=TokenPairResponse)
async def login(
    payload: LoginRequest, service: AuthenticationServiceDependency
) -> TokenPairResponse:
    tokens = await service.login(login=payload.login, password=payload.password)
    return TokenPairResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )

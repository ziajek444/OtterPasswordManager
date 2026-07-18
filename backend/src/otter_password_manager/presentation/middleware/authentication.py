from collections.abc import Awaitable, Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse, Response

from otter_password_manager.application.ports.token_service import InvalidTokenError


async def jwt_authentication_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    protected = request.url.path == "/passwords" or request.url.path.startswith("/passwords/")
    protected = protected or request.url.path.startswith("/api/v1/")
    if request.method == "OPTIONS" or not protected:
        return await call_next(request)

    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return _unauthorized("Missing bearer access token")

    try:
        payload = request.app.state.container.token_service.decode_access_token(token)
    except InvalidTokenError:
        return _unauthorized("Invalid or expired access token")

    request.state.current_user = payload
    return await call_next(request)


def _unauthorized(detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": detail},
        headers={"WWW-Authenticate": "Bearer"},
    )

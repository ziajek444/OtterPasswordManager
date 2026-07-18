from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from otter_password_manager.application.exceptions import (
    InvalidCredentialsError,
    LoginAlreadyExistsError,
    PasswordEntryNotFoundError,
    PasswordTooShortError,
    UserNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(PasswordEntryNotFoundError)
    async def password_entry_not_found(
        _: Request, exc: PasswordEntryNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Password entry {exc.args[0]} was not found"},
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials(_: Request, __: InvalidCredentialsError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid login or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found(_: Request, exc: UserNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"User {exc.args[0]} was not found"},
        )

    @app.exception_handler(LoginAlreadyExistsError)
    async def login_exists(_: Request, exc: LoginAlreadyExistsError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": f"Login '{exc.args[0]}' is already in use"},
        )

    @app.exception_handler(PasswordTooShortError)
    async def password_too_short(_: Request, exc: PasswordTooShortError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": f"Password must contain at least {exc.args[0]} characters"},
        )

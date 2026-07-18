from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from otter_password_manager.infrastructure.configuration.logging import configure_logging
from otter_password_manager.infrastructure.configuration.settings import Settings, get_settings
from otter_password_manager.infrastructure.container import ApplicationContainer
from otter_password_manager.presentation.api.login import router as login_router
from otter_password_manager.presentation.api.passwords import router as passwords_router
from otter_password_manager.presentation.api.register import router as registration_router
from otter_password_manager.presentation.api.v1.router import router as api_v1_router
from otter_password_manager.presentation.exception_handlers import register_exception_handlers
from otter_password_manager.presentation.middleware import jwt_authentication_middleware


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings)
    container = ApplicationContainer.build(resolved_settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.container = container
        try:
            yield
        finally:
            await container.close()

    app = FastAPI(
        title=resolved_settings.app_name,
        debug=resolved_settings.debug,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.middleware("http")(jwt_authentication_middleware)
    app.include_router(login_router)
    app.include_router(passwords_router)
    app.include_router(registration_router)
    app.include_router(api_v1_router, prefix=resolved_settings.api_prefix)
    register_exception_handlers(app)
    return app


app = create_app()

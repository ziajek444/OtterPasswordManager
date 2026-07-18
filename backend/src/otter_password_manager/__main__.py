import uvicorn

from otter_password_manager.infrastructure.configuration.settings import get_settings


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "otter_password_manager.main:app",
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
        reload=settings.uvicorn_reload,
        log_config=None,
    )


if __name__ == "__main__":
    run()

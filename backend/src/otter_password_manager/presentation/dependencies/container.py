from typing import Annotated

from fastapi import Depends, Request

from otter_password_manager.infrastructure.container import ApplicationContainer


def get_container(request: Request) -> ApplicationContainer:
    return request.app.state.container


ContainerDependency = Annotated[ApplicationContainer, Depends(get_container)]


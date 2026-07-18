from typing import Annotated

from fastapi import Depends

from otter_password_manager.application.services import (
    AuthenticationService,
    PasswordEntryService,
    UserService,
)
from otter_password_manager.presentation.dependencies.container import ContainerDependency


def get_user_service(container: ContainerDependency) -> UserService:
    return container.user_service


UserServiceDependency = Annotated[UserService, Depends(get_user_service)]


def get_authentication_service(container: ContainerDependency) -> AuthenticationService:
    return container.authentication_service


AuthenticationServiceDependency = Annotated[
    AuthenticationService, Depends(get_authentication_service)
]


def get_password_entry_service(container: ContainerDependency) -> PasswordEntryService:
    return container.password_entry_service


PasswordEntryServiceDependency = Annotated[
    PasswordEntryService, Depends(get_password_entry_service)
]

from typing import Annotated

from fastapi import Depends, Request

from otter_password_manager.application.dto.tokens import AccessTokenPayload


def get_current_user(request: Request) -> AccessTokenPayload:
    return request.state.current_user


CurrentUserDependency = Annotated[AccessTokenPayload, Depends(get_current_user)]

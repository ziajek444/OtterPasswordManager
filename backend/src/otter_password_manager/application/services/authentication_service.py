from collections.abc import Callable

from otter_password_manager.application.dto.tokens import TokenPair
from otter_password_manager.application.exceptions import InvalidCredentialsError
from otter_password_manager.application.ports.password_hasher import PasswordHasher
from otter_password_manager.application.ports.token_service import TokenService
from otter_password_manager.application.ports.unit_of_work import UnitOfWork


class AuthenticationService:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def login(self, *, login: str, password: str) -> TokenPair:
        async with self._unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_login(login)
            if user is None or not self._password_hasher.verify(password, user.hashed_password):
                raise InvalidCredentialsError
            return self._token_service.create_pair(user)

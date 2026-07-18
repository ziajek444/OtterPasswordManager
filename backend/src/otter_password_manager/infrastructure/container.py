from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from otter_password_manager.application.services import (
    AuthenticationService,
    PasswordEntryService,
    UserService,
)
from otter_password_manager.infrastructure.configuration.settings import Settings
from otter_password_manager.infrastructure.database.session import (
    create_engine,
    create_session_factory,
)
from otter_password_manager.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from otter_password_manager.infrastructure.security import (
    Argon2PasswordHasher,
    EncryptionService,
    JwtTokenService,
)


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    settings: Settings
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    user_service: UserService
    authentication_service: AuthenticationService
    token_service: JwtTokenService
    encryption_service: EncryptionService
    password_entry_service: PasswordEntryService

    @classmethod
    def build(cls, settings: Settings) -> "ApplicationContainer":
        engine = create_engine(settings.database_url, echo=settings.debug)
        session_factory = create_session_factory(engine)
        password_hasher = Argon2PasswordHasher()
        token_service = JwtTokenService(
            secret=settings.jwt_secret,
            access_token_minutes=settings.access_token_expire_minutes,
            refresh_token_days=settings.refresh_token_expire_days,
        )
        def unit_of_work_factory() -> SqlAlchemyUnitOfWork:
            return SqlAlchemyUnitOfWork(session_factory)

        encryption_service = EncryptionService(settings.encryption_key)
        return cls(
            settings=settings,
            engine=engine,
            session_factory=session_factory,
            user_service=UserService(unit_of_work_factory, password_hasher),
            authentication_service=AuthenticationService(
                unit_of_work_factory, password_hasher, token_service
            ),
            token_service=token_service,
            encryption_service=encryption_service,
            password_entry_service=PasswordEntryService(
                unit_of_work_factory, encryption_service
            ),
        )

    async def close(self) -> None:
        await self.engine.dispose()

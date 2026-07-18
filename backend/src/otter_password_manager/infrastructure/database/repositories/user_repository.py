from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from otter_password_manager.domain.entities.user import User
from otter_password_manager.domain.repositories.user_repository import UserRepository
from otter_password_manager.infrastructure.database.models.user_model import UserModel


def _to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        login=model.login,
        hashed_password=model.hashed_password,
        created_at=model.created_at,
    )


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, login: str, hashed_password: str) -> User:
        model = UserModel(login=login, hashed_password=hashed_password)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_domain(model)

    async def get_by_id(self, user_id: int) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _to_domain(model) if model else None

    async def get_by_login(self, login: str) -> User | None:
        model = await self._session.scalar(select(UserModel).where(UserModel.login == login))
        return _to_domain(model) if model else None

    async def list(self, *, offset: int, limit: int) -> list[User]:
        result = await self._session.scalars(
            select(UserModel).order_by(UserModel.id).offset(offset).limit(limit)
        )
        return [_to_domain(model) for model in result]

    async def update(
        self, user: User, *, login: str | None, hashed_password: str | None
    ) -> User:
        model = await self._session.get(UserModel, user.id)
        if model is None:
            raise RuntimeError("User disappeared during the transaction")
        if login is not None:
            model.login = login
        if hashed_password is not None:
            model.hashed_password = hashed_password
        await self._session.flush()
        await self._session.refresh(model)
        return _to_domain(model)

    async def delete(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()


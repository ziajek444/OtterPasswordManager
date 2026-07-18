from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from otter_password_manager.presentation.dependencies.container import ContainerDependency


async def get_session(container: ContainerDependency) -> AsyncIterator[AsyncSession]:
    async with container.session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


SessionDependency = Annotated[AsyncSession, Depends(get_session)]


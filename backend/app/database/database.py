from typing import AsyncIterator, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from .core import session_maker
from .methods.base import BaseDatabaseDep


dependent_type = TypeVar('dependent_type', bound=BaseDatabaseDep)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_maker() as session:
        yield session


def sql_helper_factory(_dep: type[dependent_type]):
    async def dep(session: Annotated[AsyncSession, Depends(get_session)] = None) -> dependent_type:
        if session is None:
            async with session_maker() as session:
                instance = _dep(session)
                yield instance
        else:
            instance = _dep(session)
            yield instance

    return dep


__all__ = [
    'sql_helper_factory'
]

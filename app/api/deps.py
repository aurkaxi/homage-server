from typing import Annotated, AsyncGenerator

from fastapi import Depends
from surrealdb import (
    AsyncHttpSurrealConnection,
    AsyncWsSurrealConnection,
    AsyncSurreal,
)

from ..core.config import settings


async def get_db() -> AsyncGenerator[
    AsyncWsSurrealConnection | AsyncHttpSurrealConnection, None,
]:
    async with AsyncSurreal(settings.SURREALDB_URL) as db:
        await db.signin(
            {
                "username": settings.SURREALDB_USER,
                "password": settings.SURREALDB_PASS,
            }
        )
        await db.use(
            settings.SURREALDB_NS,
            settings.SURREALDB_DB,
        )
        yield db


DbDep = Annotated[
    AsyncWsSurrealConnection | AsyncHttpSurrealConnection,
    Depends(get_db),
]

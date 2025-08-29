from typing import Annotated, Generator

from fastapi import Depends
from surrealdb import (
    BlockingHttpSurrealConnection,
    BlockingWsSurrealConnection,
    Surreal,
)

from ..core.config import settings


def get_db() -> Generator[
    BlockingWsSurrealConnection | BlockingHttpSurrealConnection, None, None
]:
    with Surreal(settings.SURREALDB_URL) as db:
        db.signin(
            {
                "username": settings.SURREALDB_USER,
                "password": settings.SURREALDB_PASS,
            }
        )
        db.use(
            settings.SURREALDB_NS,
            settings.SURREALDB_DB,
        )
        yield db


DbDep = Annotated[
    BlockingWsSurrealConnection | BlockingHttpSurrealConnection,
    Depends(get_db),
]

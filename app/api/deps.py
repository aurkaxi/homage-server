from typing import Annotated, Generator

from fastapi import Depends
from surrealdb import (
    BlockingHttpSurrealConnection,
    BlockingWsSurrealConnection,
    Surreal,
)


def get_db() -> Generator[
    BlockingWsSurrealConnection | BlockingHttpSurrealConnection, None, None
]:
    with Surreal("ws://localhost:8000/rpc") as db:
        db.signin({"username": "root", "password": "root"})
        db.use("aurka", "homage")
        yield db


DbDep = Annotated[
    BlockingWsSurrealConnection | BlockingHttpSurrealConnection,
    Depends(get_db),
]

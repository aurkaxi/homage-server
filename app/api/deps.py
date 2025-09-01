from typing import Annotated, Generator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from surrealdb import (
    BlockingHttpSurrealConnection,
    BlockingWsSurrealConnection,
    RecordID,
    Surreal,
)

from app.core import security
from app.core.config import settings
from app.models import TokenPayload, User


def get_db() -> Generator[
    BlockingWsSurrealConnection | BlockingHttpSurrealConnection, None, None
]:
    with Surreal(settings.SURREALDB_URL) as db:
        db.signin(
            {
                "username": settings.SURREALDB_USER,
                "password": settings.SURREALDB_PASS,
                "namespace": settings.SURREALDB_NS,
                "database": settings.SURREALDB_DB,
            }
        )
        yield db


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX_VERSIONED}/auth/access-token"
)
DbDep = Annotated[
    BlockingWsSurrealConnection | BlockingHttpSurrealConnection,
    Depends(get_db),
]


TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(db: DbDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = db.select(RecordID("user", token_data.sub))
    assert user is dict[any, any]
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_admin(current_user: CurrentUser) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

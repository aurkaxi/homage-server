from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, DbDep
from app.core import security
from app.core.config import settings
from app.models import Token, UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/access-token")
def login_access_token(
    session: DbDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        db=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/register", response_model=UserPublic)
def register_user(user: UserCreate, db: DbDep):
    """
    Register a new user
    """
    db_user = crud.create_user(db=db, user_create=user)
    return db_user


@router.get("/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser):
    """
    Test access token
    """
    return current_user

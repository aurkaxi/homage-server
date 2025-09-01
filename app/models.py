import uuid
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, EmailStr, Field
from surrealdb import RecordID


def uuid_from_recordID(record_id: Any) -> uuid.UUID:
    if isinstance(record_id, uuid.UUID):
        return record_id
    if isinstance(record_id, RecordID):
        return record_id.id
    if isinstance(record_id, str):
        return uuid.UUID(record_id)

    raise ValueError("Invalid RecordID")


ID = Annotated[uuid.UUID, BeforeValidator(uuid_from_recordID)]


# Shared properties
class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)
    is_admin: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase):
    # id: uuid.UUID = Field(default_factory=uuid.uuid4)
    id: ID = Field(default_factory=uuid.uuid4)
    hashed_password: str


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(BaseModel):
    message: str


# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: str | None = None


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

from app.api.deps import DbDep
from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate


async def create_user(
    *,
    db: DbDep,
    user_create: UserCreate,
) -> User:
    db_obj = User(
        **user_create.model_dump(),
        hashed_password=get_password_hash(user_create.password),
    )
    await db.create("user", db_obj.model_dump())
    return db_obj


# def update_user(*, db: DbDep, db_user: User, user_in: UserUpdate) -> Any:
#     user_data = user_in.model_dump(exclude_unset=True)
#     extra_data = {}
#     if "password" in user_data:
#         password = user_data["password"]
#         hashed_password = get_password_hash(password)
#         extra_data["hashed_password"] = hashed_password
#     db_user.sqlmodel_update(user_data, update=extra_data)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


async def get_user_by_email(*, db: DbDep, email: str) -> User | None:
    statement = await db.query(
        "SELECT * FROM user WHERE email = $email", {"email": email}
    )
    db_user = statement[0] if statement else None
    if db_user:
        return User.model_validate(db_user)
    return None


async def authenticate(*, db: DbDep, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(db=db, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

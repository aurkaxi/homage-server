from fastapi import APIRouter

from ..deps import DbDep

router = APIRouter(prefix="/tmp", tags=["tmp"])


@router.get("/ping")
async def ping(db: DbDep):
    print(await db.info())
    return {"message": "pong"}

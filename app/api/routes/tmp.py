from ..deps import DbDep
from fastapi import APIRouter

router = APIRouter(prefix="/tmp", tags=["tmp"])


@router.get("/ping")
async def ping(db: DbDep):
    print(db.info())
    return {"message": "pong"}

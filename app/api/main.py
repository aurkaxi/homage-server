from fastapi import APIRouter

from .routes import tmp

api_router = APIRouter()
api_router.include_router(tmp.router)

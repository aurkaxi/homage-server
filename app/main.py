from api.main import api_router
from core.config import settings
from fastapi import FastAPI

app = FastAPI()

app.include_router(api_router, prefix=settings.API_PREFIX_VERSIONED)

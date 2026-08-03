from fastapi import FastAPI

from app.config.settings import settings
from app.api.router import router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(router)
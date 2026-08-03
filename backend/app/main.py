from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.config.settings import settings
from app.utils.logger import logger

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Career Setu AI Server Started")

app.include_router(router)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Career Setu AI",
        "version": settings.APP_VERSION,
        "status": "Running"
    }
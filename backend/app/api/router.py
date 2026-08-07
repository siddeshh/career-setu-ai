from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.users import router as user_router

router = APIRouter()

router.include_router(
    health_router, 
    tags=["Health"]
)

router.include_router(
    user_router,
    tags=["Users"],
)
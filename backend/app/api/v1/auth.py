from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# POST /auth/register
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return register_user(db, user)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    

# POST /auth/login
@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:

        token = login_user(
            db,
            login_data.email,
            login_data.password,
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }

    except ValueError as e:

        raise HTTPException(
            status_code=401,
            detail=str(e),
        )
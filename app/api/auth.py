from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import UserRegisterRequest, UserResponse, UserLoginRequest, TokenResponse
from app.services.auth_service import register_user, login_user


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    return login_user(db, login_data)
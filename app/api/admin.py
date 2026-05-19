from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserResponse


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK
)
def get_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    return db.query(User).all()
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.users_model import User
from app.schemas.users_schema import UserCreate, UserCreateSuccess
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserCreateSuccess)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserCreateSuccess:
    db_user = User(name=user.name,
                   mobile=user.mobile,
                   email=user.email,
                   hashed_password=user.password,
                   is_active=user.is_active)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

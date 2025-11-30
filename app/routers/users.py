from typing import Annotated, List

from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.routers.auth import get_current_user
from app.models.users_model import User
from app.schemas.users_schema import UserCreate, UserResponse
from fastapi import APIRouter, HTTPException
from app.services import users_service

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    db_user = users_service.get_user_by_email(db, email=user.email.__str__())
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    return users_service.create_user(db=db, user=user)


@router.get("/", response_model=List[UserResponse])
def user_list(db: Annotated[Session, Depends(get_db)]) -> list[User]:
    return users_service.get_all(db)


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

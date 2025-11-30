from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.users_model import User
from app.core.security import verify_password, get_password_hash
from app.schemas.users_schema import UserCreate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    通过email获取用户信息
    :param db: 数据库会话
    :param email: 邮箱
    :return: 用户模型
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    通过email获取用户信息
    :param db: 数据库会话
    :param user_id: 邮箱
    :return: 用户模型
    """
    return db.query(User).filter(User.id == user_id).first()


def test_user() -> User:
    return User(
        id=10000,
        name="syang2501@outlook.com",
        email="syang2501@outlook.com",
        mobile="17649862173",
        hashed_password="123.com",
        is_active=True
    )


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    验证用户
    :param db: 数据库会话
    :param email: 邮箱
    :param password: 密码
    :return: 用户模型或None
    """
    user = get_user_by_email(db, email)
    if not user:
        print(f"密码错误:{email}")
        return None
    if not verify_password(password, user.hashed_password):
        print(f"密码错误:{user.email}")
        return None
    return user


def create_user(db: Session, user: UserCreate) -> User:
    """
    创建新用户
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email.__str__() if user.email else user.name,
        name=user.name,
        mobile=user.mobile,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all(db: Session) -> list[User]:
    return list(db.scalars(select(User)).all())

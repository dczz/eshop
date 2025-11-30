from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

from zoneinfo import ZoneInfo
# 确保在整个应用中使用同一个时区对象
GLOBAL_TZ_AWARE = ZoneInfo("Asia/Shanghai")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()


# 创建所有表
def create_tables():
    Base.metadata.create_all(bind=engine)

@contextmanager
def db_manager() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def get_db() -> Generator[Session, None, None]:
    with db_manager() as db:
        yield db
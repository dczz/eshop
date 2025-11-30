from fastapi import FastAPI

from .core.security import get_password_hash
from .db.database import create_tables, db_manager
from .models.users_model import User
from .routers import users, auth

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)

create_tables()

with db_manager() as db:
    test_user = db.query(User.email == "syang2501@outlook.com").first()
    if not test_user:
        test_user = User(email="syang2501@outlook.com",
                         name="songyang",
                         hashed_password=get_password_hash("123.com"),
                         is_active=True)
        print(f"创建测试用户:{test_user.__dict__}")
        db.add(test_user)
        db.commit()

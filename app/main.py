from fastapi import FastAPI

from .db.database import create_tables
from .routers import users

app = FastAPI()

create_tables()

app.include_router(users.router)

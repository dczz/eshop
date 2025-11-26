from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class UserCreate(BaseModel):
    name: str
    mobile: Optional[str] = None
    email: EmailStr
    password: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreateSuccess(BaseModel):
    id: int
    name: str
    mobile: Optional[str] = None
    email: EmailStr
    is_active: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True)
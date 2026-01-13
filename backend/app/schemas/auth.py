from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime


class UserDTO(BaseModel):
    id: int
    username: str
    email: str | None
    is_active: bool
    is_admin: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    password: str
    email: str | None = None
    captcha_id: str | None = None
    captcha_code: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class UserChangePassword(BaseModel):
    username: str
    old_password: str
    new_password: str
    captcha_id: str | None = None
    captcha_code: str | None = None

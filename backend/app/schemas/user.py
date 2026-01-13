from pydantic import BaseModel

class UserUpdateStatus(BaseModel):
    is_active: bool

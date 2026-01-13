from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SystemSettingBase(BaseModel):
    key: str
    value: Optional[str] = None
    description: Optional[str] = None

class SystemSettingCreate(SystemSettingBase):
    pass

class SystemSettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None

class SystemSetting(SystemSettingBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True

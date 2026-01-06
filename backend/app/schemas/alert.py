from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AlertOut(BaseModel):
    id: int
    name: str
    symbol: str
    condition: str
    threshold: float | None
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertCreate(BaseModel):
    name: str
    symbol: str
    condition: str
    threshold: float

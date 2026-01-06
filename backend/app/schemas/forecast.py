from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ForecastOut(BaseModel):
    id: int
    symbol: str
    timeframe: str
    ts: datetime
    horizon: int
    value: float
    lower: float | None
    upper: float | None

    model_config = ConfigDict(from_attributes=True)


class ForecastPointOut(BaseModel):
    ts: datetime
    value: float
    lower: float | None = None
    upper: float | None = None

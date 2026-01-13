from pydantic import BaseModel, ConfigDict
from datetime import datetime


class PriceOut(BaseModel):
    id: int
    symbol: str
    timeframe: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PriceDetailedOut(BaseModel):
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    created_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class PricePointOut(BaseModel):
    ts: datetime
    value: float
    created_at: datetime | None = None


class PriceDetailedPagedOut(BaseModel):
    total: int
    items: list[PriceDetailedOut]

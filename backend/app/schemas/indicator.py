from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class IndicatorOut(BaseModel):
    id: int
    symbol: str
    timeframe: str
    ts: datetime
    name: str
    value: float

    model_config = ConfigDict(from_attributes=True)


class IndicatorPointOut(BaseModel):
    ts: datetime
    value: float

class IndicatorSummaryItem(BaseModel):
    name: str
    value: float
    signal: str  # "buy", "sell", "neutral"
    desc: str
    unit: str | None = None

class IndicatorSummary(BaseModel):
    symbol: str
    timeframe: str
    ts: datetime
    items: List[IndicatorSummaryItem]

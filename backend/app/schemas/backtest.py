from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BacktestOut(BaseModel):
    id: int
    strategy: str
    symbol: str
    timeframe: str
    start_ts: datetime
    end_ts: datetime
    sharpe: float | None
    max_drawdown: float | None
    win_rate: float | None
    annual_return: float | None
    report: str | None

    model_config = ConfigDict(from_attributes=True)

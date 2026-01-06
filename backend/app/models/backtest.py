from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from .base import Base


class Backtest(Base):
    __tablename__ = "backtests"
    id = Column(Integer, primary_key=True, index=True)
    strategy = Column(String(64), index=True, nullable=False)
    symbol = Column(String(16), index=True, nullable=False)
    timeframe = Column(String(8), index=True, nullable=False)
    start_ts = Column(DateTime, nullable=False)
    end_ts = Column(DateTime, nullable=False)
    sharpe = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    annual_return = Column(Float, nullable=True)
    report = Column(Text, nullable=True)

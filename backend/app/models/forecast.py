from sqlalchemy import Column, Integer, String, DateTime, Float
from .base import Base


class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(16), index=True, nullable=False)
    timeframe = Column(String(8), index=True, nullable=False)
    ts = Column(DateTime, index=True, nullable=False)
    horizon = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)
    lower = Column(Float, nullable=True)
    upper = Column(Float, nullable=True)

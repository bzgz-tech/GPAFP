from sqlalchemy import Column, Integer, String, DateTime, Float
from .base import Base


class Indicator(Base):
    __tablename__ = "indicators"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(16), index=True, nullable=False)
    timeframe = Column(String(8), index=True, nullable=False)
    ts = Column(DateTime, index=True, nullable=False)
    name = Column(String(32), index=True, nullable=False)
    value = Column(Float, nullable=False)

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from .base import Base


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    symbol = Column(String(16), index=True, nullable=False)
    condition = Column(String(128), nullable=False)
    threshold = Column(Float, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False)

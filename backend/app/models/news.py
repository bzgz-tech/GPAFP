from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .base import Base

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    source = Column(String(64), nullable=True)
    url = Column(String(512), nullable=True)
    published_at = Column(DateTime, index=True)
    impact = Column(String(16), default="Neutral") # Bullish, Bearish, Neutral
    category = Column(String(32), index=True) # Policy, Data, Geopolitics
    created_at = Column(DateTime, server_default=func.now())

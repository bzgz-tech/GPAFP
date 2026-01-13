from sqlalchemy import Column, Integer, String, Text, DateTime
from .base import Base
from datetime import datetime

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(128), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(String(256), nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

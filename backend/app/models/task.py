from sqlalchemy import Column, String, DateTime, Integer, Text
from app.models.base import Base

class TaskStatus(Base):
    __tablename__ = "task_status"

    name = Column(String(50), primary_key=True, index=True)
    last_run = Column(DateTime)
    inserted = Column(Integer, default=0)
    total_runs = Column(Integer, default=0)
    error = Column(Text, nullable=True)

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    feedback_type = Column(String(50), nullable=False)  # 'bug', 'improvement'
    status = Column(String(50), default='pending')  # 'pending', 'adopted', 'resolved', 'closed'
    reply = Column(Text, nullable=True)
    attachments = Column(Text, default="[]")  # JSON list of attachments
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User")
    comments = relationship("FeedbackComment", back_populates="feedback", cascade="all, delete-orphan")

class FeedbackComment(Base):
    __tablename__ = "feedback_comments"

    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    attachments = Column(Text, default="[]")  # JSON list of attachments
    created_at = Column(DateTime, default=func.now())

    feedback = relationship("Feedback", back_populates="comments")
    user = relationship("User")

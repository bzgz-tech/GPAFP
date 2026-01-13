from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime
from ..services.feedback_service import FeedbackService
from ..dao.feedback_dao import FeedbackDAO
from ..models.feedback import Feedback, FeedbackComment
from ..schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackCommentCreate

class FeedbackServiceImpl(FeedbackService):
    def __init__(self):
        self.dao = FeedbackDAO()

    def create_feedback(self, db: Session, feedback_in: FeedbackCreate, user_id: int) -> Feedback:
        feedback = Feedback(
            user_id=user_id,
            title=feedback_in.title,
            content=feedback_in.content,
            feedback_type=feedback_in.feedback_type,
            attachments=json.dumps(feedback_in.attachments) if feedback_in.attachments else "[]",
            status='pending'
        )
        return self.dao.create(db, feedback)

    def get_feedbacks(self, db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> tuple[List[Feedback], int]:
        # Public Feed - ignore user_id for list view, or optional filter
        # But per requirements: "all feedbacks visible to everyone"
        # So we default to getting all.
        feedbacks = self.dao.get_all(db, skip, limit)
        total = self.dao.count(db)
        
        # Populate username (comment_count is already set by DAO)
        for f in feedbacks:
            if f.user:
                f.username = f.user.username
                
        return feedbacks, total

    def get_feedback_detail(self, db: Session, feedback_id: int) -> Optional[Feedback]:
        feedback = self.dao.get_by_id(db, feedback_id)
        if feedback:
            if feedback.user:
                feedback.username = feedback.user.username
            if feedback.comments:
                for c in feedback.comments:
                    if c.user:
                        c.username = c.user.username
            feedback.comment_count = len(feedback.comments)
        return feedback

    def update_feedback(self, db: Session, feedback_id: int, feedback_in: FeedbackUpdate) -> Feedback:
        feedback = self.dao.get_by_id(db, feedback_id)
        if not feedback:
            return None 
        
        if feedback_in.status is not None:
            feedback.status = feedback_in.status
        if feedback_in.reply is not None:
            feedback.reply = feedback_in.reply
            
        return self.dao.update(db, feedback)

    def create_comment(self, db: Session, feedback_id: int, comment_in: FeedbackCommentCreate, user_id: int) -> FeedbackComment:
        comment = FeedbackComment(
            feedback_id=feedback_id,
            user_id=user_id,
            content=comment_in.content,
            attachments=json.dumps(comment_in.attachments) if comment_in.attachments else "[]"
        )
        new_comment = self.dao.create_comment(db, comment)
        
        # Update parent feedback updated_at
        feedback = self.dao.get_by_id(db, feedback_id)
        if feedback:
            feedback.updated_at = datetime.now()
            db.add(feedback)
            db.commit()

        if new_comment.user:
            new_comment.username = new_comment.user.username
        return new_comment

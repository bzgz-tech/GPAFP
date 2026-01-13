from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.feedback import Feedback
from ..schemas.feedback import FeedbackCreate, FeedbackUpdate

class FeedbackService:
    def create_feedback(self, db: Session, feedback_in: FeedbackCreate, user_id: int) -> Feedback:
        raise NotImplementedError

    def get_feedbacks(self, db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Feedback]:
        raise NotImplementedError

    def update_feedback(self, db: Session, feedback_id: int, feedback_in: FeedbackUpdate) -> Feedback:
        raise NotImplementedError

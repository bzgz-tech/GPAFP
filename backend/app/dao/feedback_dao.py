from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, desc, func
from typing import List, Optional
from ..models.feedback import Feedback, FeedbackComment

class FeedbackDAO:
    def create(self, db: Session, feedback: Feedback) -> Feedback:
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    def get_by_id(self, db: Session, feedback_id: int) -> Optional[Feedback]:
        stmt = select(Feedback).options(
            joinedload(Feedback.user),
            joinedload(Feedback.comments).joinedload(FeedbackComment.user)
        ).where(Feedback.id == feedback_id)
        return db.execute(stmt).unique().scalar_one_or_none()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Feedback]:
        # Optimize: Don't load all comments. Use subquery to count them.
        comment_count_subquery = select(func.count(FeedbackComment.id)).where(FeedbackComment.feedback_id == Feedback.id).scalar_subquery()
        
        stmt = select(Feedback, comment_count_subquery.label("comment_count_val")).options(
            joinedload(Feedback.user)
        ).order_by(desc(Feedback.updated_at)).offset(skip).limit(limit)
        
        results = db.execute(stmt).unique().all()
        
        feedbacks = []
        for f, count in results:
            f.comment_count = count or 0
            feedbacks.append(f)
            
        return feedbacks

    def count(self, db: Session) -> int:
        return db.query(Feedback).count()

    def get_by_user_id(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Feedback]:
        comment_count_subquery = select(func.count(FeedbackComment.id)).where(FeedbackComment.feedback_id == Feedback.id).scalar_subquery()
        
        stmt = select(Feedback, comment_count_subquery.label("comment_count_val")).options(
            joinedload(Feedback.user)
        ).where(Feedback.user_id == user_id).order_by(desc(Feedback.created_at)).offset(skip).limit(limit)
        
        results = db.execute(stmt).unique().all()
        
        feedbacks = []
        for f, count in results:
            f.comment_count = count or 0
            feedbacks.append(f)
            
        return feedbacks

    def update(self, db: Session, feedback: Feedback) -> Feedback:
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    def create_comment(self, db: Session, comment: FeedbackComment) -> FeedbackComment:
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

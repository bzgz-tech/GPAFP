from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_db, get_current_active_user
from app.services_impl.feedback_service_impl import FeedbackServiceImpl
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackUpdate, FeedbackDetailResponse, FeedbackCommentCreate, FeedbackCommentResponse
from app.models.user import User

router = APIRouter()
service = FeedbackServiceImpl()

@router.post("/", response_model=FeedbackResponse)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    提交反馈
    """
    return service.create_feedback(db, feedback_in, current_user.id)

@router.get("/", response_model=List[FeedbackResponse])
def get_feedbacks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取反馈列表（公开）。
    """
    # Now all feedbacks are public
    return service.get_feedbacks(db, skip=skip, limit=limit)

@router.get("/{feedback_id}", response_model=FeedbackDetailResponse)
def get_feedback_detail(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取反馈详情（包含评论）。
    """
    feedback = service.get_feedback_detail(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@router.post("/{feedback_id}/comments", response_model=FeedbackCommentResponse)
def create_comment(
    feedback_id: int,
    comment_in: FeedbackCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    提交评论。
    """
    # Check if feedback exists
    feedback = service.get_feedback_detail(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
        
    return service.create_comment(db, feedback_id, comment_in, current_user.id)

@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: int,
    feedback_in: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新反馈状态或回复（仅管理员）。
    """
    if current_user.username != 'admin':
         raise HTTPException(
             status_code=status.HTTP_403_FORBIDDEN,
             detail="Only admin can update feedback"
         )
         
    feedback = service.update_feedback(db, feedback_id, feedback_in)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

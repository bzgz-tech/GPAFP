from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import json

class FeedbackBase(BaseModel):
    title: str
    content: str
    feedback_type: str
    attachments: List[Dict[str, str]] = []

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    status: Optional[str] = None
    reply: Optional[str] = None

class FeedbackResponse(FeedbackBase):
    id: int
    user_id: int
    username: Optional[str] = None
    status: str
    reply: Optional[str]
    created_at: datetime
    updated_at: datetime
    comment_count: int = 0
    attachments: List[Dict[str, str]] = []

    class Config:
        from_attributes = True

    @field_validator('attachments', mode='before')
    @classmethod
    def parse_attachments(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return v

class FeedbackCommentBase(BaseModel):
    content: str
    attachments: List[Dict[str, str]] = []

class FeedbackCommentCreate(FeedbackCommentBase):
    pass

class FeedbackCommentResponse(FeedbackCommentBase):
    id: int
    feedback_id: int
    user_id: int
    username: Optional[str] = None
    created_at: datetime
    attachments: List[Dict[str, str]] = []

    class Config:
        from_attributes = True

    @field_validator('attachments', mode='before')
    @classmethod
    def parse_attachments(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return v

class FeedbackDetailResponse(FeedbackResponse):
    comments: List[FeedbackCommentResponse] = []

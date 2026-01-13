from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_admin_user
from app.dao.user_dao import UserDAO
from app.schemas.auth import UserDTO
from app.schemas.user import UserUpdateStatus
from app.models.user import User
from app.schemas.pagination import Page

router = APIRouter()
dao = UserDAO()

@router.get("/", response_model=Page[UserDTO])
def read_users(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    获取用户列表（仅管理员），分页显示。
    """
    skip = (page - 1) * page_size
    users = dao.get_all(db, skip=skip, limit=page_size)
    total = dao.count(db)
    
    return Page(
        total=total,
        items=[UserDTO.model_validate(user) for user in users],
        page=page,
        page_size=page_size
    )

@router.put("/{user_id}/status", response_model=UserDTO)
def update_user_status(
    user_id: int,
    status_in: UserUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    更新用户状态（冻结/解冻）（仅管理员）。
    """
    user = dao.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 防止管理员冻结自己
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot freeze yourself")
        
    user = dao.update_status(db, user, status_in.is_active)
    return UserDTO.model_validate(user)

from typing import Optional
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.dao.user_dao import UserDAO
from app.core.security import verify_password, create_token, hash_password
from app.core.config import settings
from app.schemas.auth import Token, UserCreate, UserDTO, UserLogin
from app.models.user import User

class AuthServiceImpl(AuthService):
    """
    认证服务实现类，处理用户注册、登录验证和 Token 生成。
    """
    def __init__(self, db: Session):
        self.db = db
        self.dao = UserDAO()

    def authenticate_user(self, login_data: UserLogin) -> Optional[UserDTO]:
        """
        验证用户登录凭据。
        
        逻辑:
            1. 根据用户名查找用户。
            2. 验证密码哈希是否匹配。
            3. 检查用户账号是否处于激活状态。
            
        返回:
            验证通过返回 UserDTO，否则返回 None。
        """
        user = self.dao.find_by_username(self.db, login_data.username)
        if not user:
            return None
        if not verify_password(login_data.password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return UserDTO.model_validate(user)

    def create_access_token(self, user: UserDTO) -> Token:
        """
        为通过验证的用户创建 JWT 访问令牌。
        """
        access_token = create_token(payload={"sub": user.username})
        return Token(access_token=access_token, token_type="bearer")

    def register_user(self, user_in: UserCreate) -> Optional[UserDTO]:
        """
        注册新用户。
        
        逻辑:
            1. 检查用户名是否已存在。
            2. 对密码进行哈希加密。
            3. 创建并保存新用户记录。
            
        返回:
            注册成功返回 UserDTO，用户名已存在返回 None。
        """
        existing_user = self.dao.find_by_username(self.db, user_in.username)
        if existing_user:
            return None
        hashed_pw = hash_password(user_in.password)
        new_user = User(
            username=user_in.username,
            hashed_password=hashed_pw,
            email=user_in.email,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        created = self.dao.create(self.db, new_user)
        return UserDTO.model_validate(created)

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        修改用户密码。
        
        逻辑:
            1. 验证旧密码是否正确。
            2. 如果正确，更新为新密码的哈希值。
            
        返回:
            修改成功返回 True，验证失败返回 False。
        """
        user = self.dao.find_by_username(self.db, username)
        if not user:
            return False
        if not verify_password(old_password, user.hashed_password):
            return False
        
        user.hashed_password = hash_password(new_password)
        self.db.add(user)
        self.db.commit()
        return True

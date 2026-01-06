from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.services_impl.auth_service_impl import AuthServiceImpl
from app.schemas.auth import Token, UserCreate, UserDTO, UserLogin
from app.models.user import User

# 创建路由实例
router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    用户登录接口，获取访问令牌。
    
    参数:
        form_data (OAuth2PasswordRequestForm): OAuth2 标准登录表单（包含用户名和密码）。
        db (Session): 数据库会话依赖。
        
    返回:
        Token: 包含访问令牌和令牌类型的对象。
        
    异常:
        HTTPException(401): 用户名或密码错误。
    """
    service = AuthServiceImpl(db)
    # 验证用户凭证
    user = service.authenticate_user(UserLogin(username=form_data.username, password=form_data.password))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 创建并返回访问令牌
    return service.create_access_token(user)

@router.post("/register", response_model=UserDTO)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    用户注册接口。
    
    参数:
        user_in (UserCreate): 用户注册信息（用户名、邮箱、密码）。
        db (Session): 数据库会话依赖。
        
    返回:
        UserDTO: 注册成功的用户信息（不含密码）。
        
    异常:
        HTTPException(400): 用户名已被注册。
    """
    service = AuthServiceImpl(db)
    user = service.register_user(user_in)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="用户名已被注册",
        )
    return user

@router.get("/me", response_model=UserDTO)
def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    获取当前登录用户的信息。
    
    参数:
        current_user (User): 通过 Token 验证后的当前用户对象。
        
    返回:
        UserDTO: 当前用户信息。
    """
    return UserDTO.model_validate(current_user)

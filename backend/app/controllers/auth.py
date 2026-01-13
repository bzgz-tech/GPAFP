from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.services_impl.auth_service_impl import AuthServiceImpl
from app.schemas.auth import Token, UserCreate, UserDTO, UserLogin, UserChangePassword
from app.models.user import User
from app.core.captcha_store import captcha_service
from app.core.security import verify_password
from fastapi import Form
import base64

# 创建路由实例
router = APIRouter()

@router.get("/captcha")
def get_captcha():
    """
    获取图形验证码
    """
    captcha_id, image_bytes = captcha_service.generate_captcha()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    return {
        "captcha_id": captcha_id,
        "image": f"data:image/png;base64,{image_b64}"
    }

@router.post("/login", response_model=Token)
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    captcha_id: str = Form(None),
    captcha_code: str = Form(None),
    db: Session = Depends(get_db),
):
    """
    用户登录接口，获取访问令牌。
    连续登录失败3次后需提供验证码。
    """
    service = AuthServiceImpl(db)
    user = service.dao.find_by_username(db, form_data.username)

    # 1. Check user existence
    if not user:
        # 为了安全，这里不应该暴露用户是否存在，但为了逻辑简单，先返回统一错误
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Check failed attempts (Threshold: 3)
    if user.failed_login_attempts >= 3:
        if not captcha_id or not captcha_code:
            raise HTTPException(
                status_code=400,
                detail="Require Captcha",
            )
        if not captcha_service.verify_captcha(captcha_id, captcha_code):
            raise HTTPException(
                status_code=400,
                detail="验证码错误或已过期",
            )

    # 3. Verify password
    if not verify_password(form_data.password, user.hashed_password):
        user.failed_login_attempts += 1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Check active status
    if not user.is_active:
        raise HTTPException(status_code=400, detail="您的账户已被冻结，请联系管理员处理")

    # 5. Success - Reset attempts
    if user.failed_login_attempts > 0:
        user.failed_login_attempts = 0
        db.commit()

    return service.create_access_token(UserDTO.model_validate(user))

@router.post("/register", response_model=UserDTO)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    用户注册接口。
    
    参数:
        user_in (UserCreate): 用户注册信息（用户名、邮箱、密码、验证码）。
        db (Session): 数据库会话依赖。
        
    返回:
        UserDTO: 注册成功的用户信息（不含密码）。
        
    异常:
        HTTPException(400): 用户名已被注册或验证码错误。
    """
    # 验证验证码
    if not captcha_service.verify_captcha(user_in.captcha_id, user_in.captcha_code):
        raise HTTPException(
            status_code=400,
            detail="验证码错误或已过期",
        )

    service = AuthServiceImpl(db)
    user = service.register_user(user_in)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="用户名已被注册",
        )
    return user

@router.post("/change-password")
def change_password(
    data: UserChangePassword,
    db: Session = Depends(get_db),
):
    """
    修改密码接口。
    """
    # 验证验证码
    if not captcha_service.verify_captcha(data.captcha_id, data.captcha_code):
        raise HTTPException(
            status_code=400,
            detail="验证码错误或已过期",
        )

    service = AuthServiceImpl(db)
    success = service.change_password(data.username, data.old_password, data.new_password)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="用户名或旧密码错误",
        )
    return {"message": "密码修改成功"}

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

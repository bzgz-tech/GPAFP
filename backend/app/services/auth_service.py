from sqlalchemy.orm import Session
from ..models.user import User


class AuthService:
    """
    认证服务接口，定义用户注册和登录的业务逻辑规范。
    """
    def register(self, db: Session, username: str, password: str, email: str | None) -> User:
        """
        注册新用户。

        参数:
            db (Session): 数据库会话。
            username (str): 用户名。
            password (str): 明文密码（应在实现中进行哈希处理）。
            email (str | None): 邮箱地址（可选）。

        返回:
            User: 创建的用户对象。
        """
        raise NotImplementedError

    def login(self, db: Session, username: str, password: str) -> str:
        """
        用户登录。

        参数:
            db (Session): 数据库会话。
            username (str): 用户名。
            password (str): 明文密码。

        返回:
            str: 访问令牌 (Token)。
        """
        raise NotImplementedError

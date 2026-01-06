from sqlalchemy.orm import Session
from ..models.alert import Alert


class AlertService:
    """
    告警服务接口，定义告警相关的业务逻辑规范。
    """
    def get_active_alerts(self, db: Session, symbol: str) -> list[Alert]:
        """
        获取指定品种的当前活跃告警。

        参数:
            db (Session): 数据库会话。
            symbol (str): 交易品种代码。

        返回:
            list[Alert]: 活跃告警列表。
        """
        raise NotImplementedError

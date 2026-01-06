from sqlalchemy.orm import Session
from ..models.price import Price


class MarketService:
    """
    市场数据服务接口，定义价格数据的查询和导入规范。
    """
    def get_latest_price(self, db: Session, symbol: str, timeframe: str) -> Price | None:
        """
        获取最新的一条价格记录。

        参数:
            db (Session): 数据库会话。
            symbol (str): 交易品种代码。
            timeframe (str): 时间周期（如 '1d', '1h'）。

        返回:
            Price | None: 最新价格对象，如果不存在则返回 None。
        """
        raise NotImplementedError

    def get_history(self, db: Session, symbol: str, timeframe: str, start_ts, end_ts=None) -> list[Price]:
        """
        获取指定时间范围内的历史价格数据。

        参数:
            db (Session): 数据库会话。
            symbol (str): 交易品种代码。
            timeframe (str): 时间周期。
            start_ts (int): 开始时间戳。
            end_ts (int, optional): 结束时间戳。

        返回:
            list[Price]: 价格数据列表。
        """
        raise NotImplementedError

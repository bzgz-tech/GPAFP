from sqlalchemy.orm import Session
from ..models.indicator import Indicator


class IndicatorService:
    """
    技术指标服务接口，定义技术指标数据的查询规范。
    """
    def get_latest_indicator(self, db: Session, symbol: str, timeframe: str, name: str) -> Indicator | None:
        """
        获取最新的一条技术指标数据。

        参数:
            db (Session): 数据库会话。
            symbol (str): 交易品种。
            timeframe (str): 时间周期。
            name (str): 指标名称（如 'RSI', 'MA'）。

        返回:
            Indicator | None: 最新指标对象。
        """
        raise NotImplementedError

    def get_history(self, db: Session, symbol: str, timeframe: str, name: str, start_ts, end_ts=None) -> list[Indicator]:
        """
        获取历史技术指标数据列表。

        参数:
            db (Session): 数据库会话。
            symbol (str): 交易品种。
            timeframe (str): 时间周期。
            name (str): 指标名称。
            start_ts (int): 开始时间戳。
            end_ts (int, optional): 结束时间戳。

        返回:
            list[Indicator]: 技术指标数据列表。
        """
        raise NotImplementedError

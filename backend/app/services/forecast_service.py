from sqlalchemy.orm import Session
from ..models.forecast import Forecast


class ForecastService:
    """
    预测服务接口，定义价格预测数据的查询规范。
    """
    def get_latest_forecast(self, db: Session, symbol: str, timeframe: str, horizon: int) -> Forecast | None:
        """
        获取最新的一条预测数据。

        参数:
            db (Session): 数据库会话。
            symbol (str): 交易品种。
            timeframe (str): 时间周期。
            horizon (int): 预测跨度。

        返回:
            Forecast | None: 最新预测对象。
        """
        raise NotImplementedError

    def get_history(self, db: Session, symbol: str, timeframe: str, horizon: int, start_ts, end_ts=None) -> list[Forecast]:
        """
        获取历史预测数据列表。

        参数:
            db (Session): 数据库会话。
            symbol (str): 交易品种。
            timeframe (str): 时间周期。
            horizon (int): 预测跨度。
            start_ts (int): 开始时间戳。
            end_ts (int, optional): 结束时间戳。

        返回:
            list[Forecast]: 预测数据列表。
        """
        raise NotImplementedError

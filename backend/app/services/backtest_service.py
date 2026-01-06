from sqlalchemy.orm import Session
from ..models.backtest import Backtest


class BacktestService:
    """
    回测服务接口，定义回测结果查询的业务逻辑规范。
    """
    def get_latest_backtest(self, db: Session, strategy: str, symbol: str, timeframe: str) -> Backtest | None:
        """
        获取最新的回测结果。

        参数:
            db (Session): 数据库会话。
            strategy (str): 策略名称。
            symbol (str): 交易品种。
            timeframe (str): 时间周期。

        返回:
            Backtest | None: 最新回测结果对象，若无则返回 None。
        """
        raise NotImplementedError

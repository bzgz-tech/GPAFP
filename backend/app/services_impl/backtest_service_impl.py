from sqlalchemy.orm import Session
from ..services.backtest_service import BacktestService
from ..dao.backtest_dao import BacktestDAO
from ..models.backtest import Backtest


class BacktestServiceImpl(BacktestService):
    """
    回测服务实现类，负责获取策略回测结果。
    目前主要用于数据查询，实际的回测计算逻辑可能在单独的任务或外部服务中。
    """
    def __init__(self, backtest_dao: BacktestDAO):
        self.backtest_dao = backtest_dao

    def get_latest_backtest(self, db: Session, strategy: str, symbol: str, timeframe: str) -> Backtest | None:
        """
        获取指定策略、品种和时间周期的最新回测结果。
        """
        return self.backtest_dao.get_latest(db, strategy, symbol, timeframe)

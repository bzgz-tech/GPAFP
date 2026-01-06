from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from ..models.backtest import Backtest


class BacktestDAO:
    def get_latest(self, db: Session, strategy: str, symbol: str, timeframe: str) -> Backtest | None:
        stmt = select(Backtest).where(Backtest.strategy == strategy, Backtest.symbol == symbol, Backtest.timeframe == timeframe).order_by(desc(Backtest.end_ts)).limit(1)
        return db.execute(stmt).scalar_one_or_none()

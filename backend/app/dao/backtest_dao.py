from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from ..models.backtest import Backtest


class BacktestDAO:
    def get_latest(self, db: Session, strategy: str, symbol: str, timeframe: str) -> Backtest | None:
        stmt = select(Backtest).where(Backtest.strategy == strategy, Backtest.symbol == symbol, Backtest.timeframe == timeframe).order_by(desc(Backtest.end_ts)).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    def get_all(self, db: Session, skip: int = 0, limit: int = 20) -> tuple[list[Backtest], int]:
        stmt = select(Backtest).order_by(desc(Backtest.created_at)).offset(skip).limit(limit)
        items = db.execute(stmt).scalars().all()
        
        # Count
        count_stmt = select(func.count()).select_from(Backtest)
        total = db.execute(count_stmt).scalar()
        
        return items, total

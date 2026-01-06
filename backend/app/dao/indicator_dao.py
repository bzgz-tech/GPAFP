from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from ..models.indicator import Indicator


class IndicatorDAO:
    def get_latest(self, db: Session, symbol: str, timeframe: str, name: str) -> Indicator | None:
        stmt = select(Indicator).where(Indicator.symbol == symbol, Indicator.timeframe == timeframe, Indicator.name == name).order_by(desc(Indicator.ts)).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    def get_range(self, db: Session, symbol: str, timeframe: str, name: str, start_ts, end_ts=None) -> list[Indicator]:
        stmt = select(Indicator).where(Indicator.symbol == symbol, Indicator.timeframe == timeframe, Indicator.name == name, Indicator.ts >= start_ts)
        if end_ts is not None:
            stmt = stmt.where(Indicator.ts <= end_ts)
        stmt = stmt.order_by(Indicator.ts.asc())
        return list(db.execute(stmt).scalars().all())

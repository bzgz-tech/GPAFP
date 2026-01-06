from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from ..models.forecast import Forecast


class ForecastDAO:
    def get_latest(self, db: Session, symbol: str, timeframe: str, horizon: int) -> Forecast | None:
        stmt = select(Forecast).where(Forecast.symbol == symbol, Forecast.timeframe == timeframe, Forecast.horizon == horizon).order_by(desc(Forecast.ts)).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    def get_range(self, db: Session, symbol: str, timeframe: str, horizon: int, start_ts, end_ts=None) -> list[Forecast]:
        stmt = select(Forecast).where(Forecast.symbol == symbol, Forecast.timeframe == timeframe, Forecast.horizon == horizon, Forecast.ts >= start_ts)
        if end_ts is not None:
            stmt = stmt.where(Forecast.ts <= end_ts)
        stmt = stmt.order_by(Forecast.ts.asc())
        return list(db.execute(stmt).scalars().all())

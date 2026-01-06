from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from ..models.price import Price
from sqlalchemy import func


class PriceDAO:
    def get_latest(self, db: Session, symbol: str, timeframe: str) -> Price | None:
        stmt = select(Price).where(Price.symbol == symbol, Price.timeframe == timeframe).order_by(desc(Price.ts)).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    def get_range(self, db: Session, symbol: str, timeframe: str, start_ts=None, end_ts=None) -> list[Price]:
        stmt = select(Price).where(Price.symbol == symbol, Price.timeframe == timeframe)
        if start_ts is not None:
            stmt = stmt.where(Price.ts >= start_ts)
        if end_ts is not None:
            stmt = stmt.where(Price.ts <= end_ts)
        stmt = stmt.order_by(Price.ts.asc())
        return list(db.execute(stmt).scalars().all())

    def bulk_insert(self, db: Session, rows: list[Price]) -> int:
        for r in rows:
            db.add(r)
        db.commit()
        return len(rows)

    def get_max_ts(self, db: Session, symbol: str, timeframe: str):
        stmt = select(func.max(Price.ts)).where(Price.symbol == symbol, Price.timeframe == timeframe)
        return db.execute(stmt).scalar_one()

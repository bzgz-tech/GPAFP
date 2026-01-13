from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from ..models.alert import Alert


class AlertDAO:
    def get_active(self, db: Session, symbol: str, skip: int = 0, limit: int = 20) -> list[Alert]:
        stmt = select(Alert).where(Alert.symbol == symbol, Alert.active == True).order_by(desc(Alert.created_at)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_active(self, db: Session, symbol: str) -> int:
        stmt = select(Alert).where(Alert.symbol == symbol, Alert.active == True)
        # Using a more efficient count query if possible, but for now list len is fine for small scale or count()
        # SQLAlchemy 1.4+ count style:
        from sqlalchemy import func
        stmt_count = select(func.count()).select_from(Alert).where(Alert.symbol == symbol, Alert.active == True)
        return db.execute(stmt_count).scalar()

    def create(self, db: Session, alert: Alert) -> Alert:
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    def delete(self, db: Session, alert_id: int):
        stmt = select(Alert).where(Alert.id == alert_id)
        alert = db.execute(stmt).scalars().first()
        if alert:
            db.delete(alert)
            db.commit()

    def update_status(self, db: Session, alert_id: int, active: bool):
        stmt = select(Alert).where(Alert.id == alert_id)
        alert = db.execute(stmt).scalars().first()
        if alert:
            alert.active = active
            db.commit()

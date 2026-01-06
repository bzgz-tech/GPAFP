from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from ..models.alert import Alert


class AlertDAO:
    def get_active(self, db: Session, symbol: str) -> list[Alert]:
        stmt = select(Alert).where(Alert.symbol == symbol, Alert.active == True).order_by(desc(Alert.created_at))
        return list(db.execute(stmt).scalars().all())

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

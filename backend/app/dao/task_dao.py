from sqlalchemy.orm import Session
from app.models.task import TaskStatus
from datetime import datetime

class TaskDAO:
    def update(self, db: Session, name: str, inserted: int = 0, error: str = None):
        task = db.query(TaskStatus).filter(TaskStatus.name == name).first()
        if not task:
            task = TaskStatus(name=name, total_runs=0)
            db.add(task)
        
        task.last_run = datetime.utcnow()
        task.inserted = inserted
        task.error = error
        task.total_runs += 1
        db.commit()
        db.refresh(task)
        return task

    def get_all(self, db: Session):
        return db.query(TaskStatus).all()

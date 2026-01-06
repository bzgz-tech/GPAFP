import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.db import SessionLocal
from app.dao.task_dao import TaskDAO

def check_tasks():
    db = SessionLocal()
    try:
        dao = TaskDAO()
        tasks = dao.get_all(db)
        for task in tasks:
            print(f"Task: {task.name}, Last run: {task.last_run}, Inserted: {task.inserted}, Error: {task.error}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_tasks()

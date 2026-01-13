from app.core.db import engine
from sqlalchemy import text
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

def add_column():
    with engine.connect() as conn:
        print("Adding columns...")
        
        try:
            conn.execute(text("ALTER TABLE feedbacks ADD COLUMN attachments TEXT"))
            conn.execute(text("UPDATE feedbacks SET attachments = '[]' WHERE attachments IS NULL"))
            print("Added attachments to feedbacks")
        except Exception as e:
            print(f"feedbacks error: {e}")
            
        try:
            conn.execute(text("ALTER TABLE feedback_comments ADD COLUMN attachments TEXT"))
            conn.execute(text("UPDATE feedback_comments SET attachments = '[]' WHERE attachments IS NULL"))
            print("Added attachments to feedback_comments")
        except Exception as e:
            print(f"feedback_comments error: {e}")
            
        conn.commit()
        print("Done.")

if __name__ == "__main__":
    add_column()

from sqlalchemy.orm import Session
from ..models.news import News
from ..schemas.news import NewsCreate
from typing import List, Optional

class NewsDAO:
    def get_latest(self, db: Session, skip: int = 0, limit: int = 10, category: Optional[str] = None) -> List[News]:
        query = db.query(News)
        if category:
            query = query.filter(News.category == category)
        return query.order_by(News.published_at.desc()).offset(skip).limit(limit).all()

    def count(self, db: Session, category: Optional[str] = None) -> int:
        query = db.query(News)
        if category:
            query = query.filter(News.category == category)
        return query.count()

    def create(self, db: Session, obj_in: NewsCreate) -> News:
        db_obj = News(
            title=obj_in.title,
            summary=obj_in.summary,
            source=obj_in.source,
            url=obj_in.url,
            published_at=obj_in.published_at,
            impact=obj_in.impact,
            category=obj_in.category
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def bulk_create(self, db: Session, objs_in: List[NewsCreate]) -> int:
        db_objs = [
            News(
                title=obj.title,
                summary=obj.summary,
                source=obj.source,
                url=obj.url,
                published_at=obj.published_at,
                impact=obj.impact,
                category=obj.category
            ) for obj in objs_in
        ]
        db.bulk_save_objects(db_objs)
        db.commit()
        return len(db_objs)

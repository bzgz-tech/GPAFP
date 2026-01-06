from sqlalchemy.orm import Session
from ..schemas.news import News, NewsCreate
from typing import List, Optional

class NewsService:
    def get_latest_news(self, db: Session, limit: int = 20, category: Optional[str] = None) -> List[News]:
        raise NotImplementedError

    def fetch_and_update(self, db: Session) -> int:
        """
        Fetch news from external sources and update database.
        """
        raise NotImplementedError

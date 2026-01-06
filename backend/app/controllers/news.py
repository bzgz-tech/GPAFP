from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.deps import get_db
from ..schemas.news import News
from ..dao.news_dao import NewsDAO
from ..services_impl.news_service_impl import NewsServiceImpl

router = APIRouter()

def get_news_service(db: Session = Depends(get_db)) -> NewsServiceImpl:
    return NewsServiceImpl(NewsDAO())

@router.get("/", response_model=List[News])
def get_news(
    limit: int = 20,
    category: Optional[str] = Query(None, enum=["Policy", "Data", "Geopolitics"]),
    db: Session = Depends(get_db),
    service: NewsServiceImpl = Depends(get_news_service)
):
    # Trigger a mock update first (in production this would be a background task)
    service.fetch_and_update(db)
    return service.get_latest_news(db, limit=limit, category=category)

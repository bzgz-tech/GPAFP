from sqlalchemy.orm import Session
from ..services.news_service import NewsService
from ..dao.news_dao import NewsDAO
from ..schemas.news import NewsCreate
from datetime import datetime, timedelta
import random

class NewsServiceImpl(NewsService):
    def __init__(self, news_dao: NewsDAO):
        self.news_dao = news_dao

    def get_latest_news(self, db: Session, limit: int = 20, category: str | None = None):
        return self.news_dao.get_latest(db, limit=limit, category=category)

    def fetch_and_update(self, db: Session) -> int:
        # Mock implementation: Generate some fake news if DB is empty or just add some new ones
        # In a real app, this would call an external API or scrape a website
        
        current_news = self.news_dao.get_latest(db, limit=1)
        if current_news and (datetime.utcnow() - current_news[0].created_at).seconds < 3600:
            return 0 # Update at most once per hour for mock

        mock_news = [
            {
                "title": "美联储暗示可能在下个季度暂停加息",
                "summary": "美联储主席在最新的新闻发布会上表示，通胀数据正在改善，未来货币政策将更加依赖数据。",
                "source": "FedNews",
                "impact": "Bullish",
                "category": "Policy"
            },
            {
                "title": "美国非农就业数据超预期",
                "summary": "最新公布的非农就业新增人数为30万人，远超预期的20万人，显示劳动力市场依然强劲。",
                "source": "DataDaily",
                "impact": "Bearish",
                "category": "Data"
            },
            {
                "title": "中东局势紧张加剧，避险情绪升温",
                "summary": "由于地缘政治冲突升级，市场避险需求增加，黄金价格获得支撑。",
                "source": "GlobalTimes",
                "impact": "Bullish",
                "category": "Geopolitics"
            },
            {
                "title": "欧洲央行维持利率不变",
                "summary": "欧洲央行决定维持主要再融资利率不变，符合市场预期。",
                "source": "ECB",
                "impact": "Neutral",
                "category": "Policy"
            }
        ]
        
        new_items = []
        for item in mock_news:
            # Randomize time slightly
            pub_time = datetime.utcnow() - timedelta(minutes=random.randint(1, 120))
            new_items.append(NewsCreate(
                title=item["title"],
                summary=item["summary"],
                source=item["source"],
                url="http://example.com",
                published_at=pub_time,
                impact=item["impact"],
                category=item["category"]
            ))
            
        return self.news_dao.bulk_create(db, new_items)

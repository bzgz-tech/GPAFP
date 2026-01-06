from app.core.db import SessionLocal
from app.services_impl.forecast_service_impl import ForecastServiceImpl
from app.dao.forecast_dao import ForecastDAO
from app.dao.price_dao import PriceDAO
from app.dao.task_dao import TaskDAO
import logging

logger = logging.getLogger(__name__)

def job_generate_forecast():
    """生成价格预测。"""
    db = SessionLocal()
    task_dao = TaskDAO()
    try:
        service = ForecastServiceImpl(ForecastDAO(), PriceDAO())
        # 生成未来7天的日线预测
        result = service.predict_next_days(db, "XAUUSD", days=7)
        count = len(result) if result else 0
        task_dao.update(db, "forecast_generation", inserted=count, error=None)
    except Exception as e:
        logger.error(f"预测生成失败: {e}")
        task_dao.update(db, "forecast_generation", inserted=0, error=str(e))
    finally:
        db.close()

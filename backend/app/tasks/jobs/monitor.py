from app.core.db import SessionLocal
from app.services_impl.alert_service_impl import AlertServiceImpl
from app.dao.alert_dao import AlertDAO
from app.dao.price_dao import PriceDAO
from app.dao.task_dao import TaskDAO
import logging

logger = logging.getLogger(__name__)

def job_check_alerts():
    """检查价格告警。"""
    db = SessionLocal()
    task_dao = TaskDAO()
    try:
        alert_service = AlertServiceImpl(AlertDAO(), PriceDAO())
        # 确保默认设置存在
        alert_service.initialize_defaults(db, "XAUUSD")
        
        triggered = alert_service.check_alerts(db, "XAUUSD")
        count = len(triggered) if triggered else 0
        task_dao.update(db, "alert_check", inserted=count, error=None)
    except Exception as e:
        logger.error(f"告警检查失败: {e}")
        task_dao.update(db, "alert_check", inserted=0, error=str(e))
    finally:
        db.close()

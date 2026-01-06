from app.core.db import SessionLocal
from app.services_impl.indicator_service_impl import IndicatorServiceImpl
from app.dao.indicator_dao import IndicatorDAO
from app.dao.price_dao import PriceDAO
from app.dao.task_dao import TaskDAO
import logging

logger = logging.getLogger(__name__)

def job_calculate_indicators(timeframe: str):
    """计算指定周期的技术指标。"""
    db = SessionLocal()
    task_dao = TaskDAO()
    task_id = f"indicator_calculation_{timeframe}"
    try:
        service = IndicatorServiceImpl(IndicatorDAO(), PriceDAO())
        updated_count = 0
        # MA, MACD, RSI are standard. KDJ needs specific components.
        # Also add SUPPORT and RESISTANCE
        indicators = ["RSI", "MACD", "MA", "KDJ_K", "KDJ_D", "KDJ_J", "SUPPORT", "RESISTANCE"]
        for name in indicators:
            # 重新计算指标
            service.calculate_and_save(db, "XAUUSD", timeframe, name)
            updated_count += 1
                
        task_dao.update(db, task_id, inserted=updated_count, error=None)
    except Exception as e:
        logger.error(f"周期 {timeframe} 的指标计算失败: {e}")
        task_dao.update(db, task_id, inserted=0, error=str(e))
    finally:
        db.close()

def job_calculate_indicators_1m():
    job_calculate_indicators("1m")

def job_calculate_indicators_1h():
    job_calculate_indicators("1h")

def job_calculate_indicators_1d():
    job_calculate_indicators("1d")

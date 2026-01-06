from app.core.db import SessionLocal
from app.services_impl.market_service_impl import MarketServiceImpl
from app.dao.price_dao import PriceDAO
from app.dao.task_dao import TaskDAO
import logging

logger = logging.getLogger(__name__)

def job_fetch_realtime_data():
    """获取用于实时监控的1分钟数据。"""
    db = SessionLocal()
    task_dao = TaskDAO()
    try:
        service = MarketServiceImpl(PriceDAO())
        # 获取最新的1分钟数据
        # 使用 window="1d" 确保有足够的上下文，同时避免负载过高
        count = service.import_history(db, symbol="XAUUSD", timeframe="1m", window="1d")
        task_dao.update(db, "realtime_data_fetch", inserted=count, error=None)
    except Exception as e:
        logger.error(f"实时数据获取失败: {e}")
        task_dao.update(db, "realtime_data_fetch", inserted=0, error=str(e))
    finally:
        db.close()

def job_fetch_hourly_data():
    """获取1小时数据。"""
    db = SessionLocal()
    task_dao = TaskDAO()
    try:
        service = MarketServiceImpl(PriceDAO())
        count = service.import_history(db, symbol="XAUUSD", timeframe="1h", window="1d")
        task_dao.update(db, "hourly_data_fetch", inserted=count, error=None)
    except Exception as e:
        logger.error(f"小时数据获取失败: {e}")
        task_dao.update(db, "hourly_data_fetch", inserted=0, error=str(e))
    finally:
        db.close()

def job_fetch_daily_data():
    """获取日线数据。"""
    db = SessionLocal()
    task_dao = TaskDAO()
    try:
        service = MarketServiceImpl(PriceDAO())
        count = service.import_history(db, symbol="XAUUSD", timeframe="1d", window="1m")
        task_dao.update(db, "daily_data_fetch", inserted=count, error=None)
    except Exception as e:
        logger.error(f"日线数据获取失败: {e}")
        task_dao.update(db, "daily_data_fetch", inserted=0, error=str(e))
    finally:
        db.close()

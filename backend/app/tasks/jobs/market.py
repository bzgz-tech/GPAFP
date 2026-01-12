from app.core.db import SessionLocal
from app.services_impl.market_service_impl import MarketServiceImpl
from app.dao.price_dao import PriceDAO
from app.dao.task_dao import TaskDAO
import logging

logger = logging.getLogger(__name__)

# 定义需要获取的市场代码：黄金、美元指数、美债收益率、原油
SYMBOLS = ["XAUUSD", "DX-Y.NYB", "^TNX", "CL=F"]

def fetch_all_symbols(db, service, timeframe, window):
    total_count = 0
    errors = []
    for symbol in SYMBOLS:
        try:
            count = service.import_history(db, symbol=symbol, timeframe=timeframe, window=window)
            total_count += count
        except Exception as e:
            msg = f"{symbol}: {e}"
            logger.error(f"Failed to fetch {timeframe} data for {msg}")
            errors.append(msg)
    return total_count, "; ".join(errors) if errors else None

def job_fetch_realtime_data():
    """获取用于实时监控的1分钟数据。"""
    db = SessionLocal()
    task_dao = TaskDAO()
    try:
        service = MarketServiceImpl(PriceDAO())
        # 获取最新的1分钟数据
        count, error = fetch_all_symbols(db, service, "1m", "1d")
        task_dao.update(db, "realtime_data_fetch", inserted=count, error=error)
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
        count, error = fetch_all_symbols(db, service, "1h", "1d")
        task_dao.update(db, "hourly_data_fetch", inserted=count, error=error)
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
        count, error = fetch_all_symbols(db, service, "1d", "1m")
        task_dao.update(db, "daily_data_fetch", inserted=count, error=error)
    except Exception as e:
        logger.error(f"日线数据获取失败: {e}")
        task_dao.update(db, "daily_data_fetch", inserted=0, error=str(e))
    finally:
        db.close()

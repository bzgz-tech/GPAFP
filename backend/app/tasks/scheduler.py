from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone
import logging
from threading import Thread
import time

# 导入任务
from app.tasks.jobs.market import job_fetch_realtime_data, job_fetch_hourly_data, job_fetch_daily_data
from app.tasks.jobs.analysis import job_calculate_indicators_1m, job_calculate_indicators_1h, job_calculate_indicators_1d
from app.tasks.jobs.monitor import job_check_alerts
from app.tasks.jobs.forecast import job_generate_forecast
from app.services_impl.news_service_impl import NewsServiceImpl
from app.dao.news_dao import NewsDAO
from app.core.db import SessionLocal

logger = logging.getLogger(__name__)

def job_fetch_news():
    """Fetch news periodically"""
    db = SessionLocal()
    try:
        service = NewsServiceImpl(NewsDAO())
        count = service.fetch_and_update(db)
        if count > 0:
            logger.info(f"Fetched {count} new news items")
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
    finally:
        db.close()

def run_startup_jobs():
    """在启动时立即执行一次所有任务。"""
    # 如有需要，允许数据库和应用有一些启动缓冲时间，但“立即”通常意味着尽快执行
    time.sleep(2) 
    logger.info("正在运行启动任务...")
    try:
        # 按隐式依赖顺序执行（数据 -> 分析 -> 预测/告警）
        
        logger.info("启动：获取实时数据")
        job_fetch_realtime_data()
        
        logger.info("启动：获取小时数据")
        job_fetch_hourly_data()
        
        logger.info("启动：获取日线数据")
        job_fetch_daily_data()
        
        logger.info("启动：计算指标 (1m, 1h, 1d)")
        job_calculate_indicators_1m()
        job_calculate_indicators_1h()
        job_calculate_indicators_1d()
        
        logger.info("启动：获取新闻")
        job_fetch_news()
        
        logger.info("启动：生成预测")
        job_generate_forecast()
        
        logger.info("启动：检查告警")
        job_check_alerts()
        
        logger.info("启动任务已完成。")
    except Exception as e:
        logger.error(f"启动任务错误: {e}")

def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    
    # 1. 市场数据任务
    # 实时：每1分钟
    scheduler.add_job(
        job_fetch_realtime_data,
        IntervalTrigger(minutes=1),
        id="realtime_data_fetch",
        replace_existing=True
    )
    
    # 小时：每30分钟
    scheduler.add_job(
        job_fetch_hourly_data,
        IntervalTrigger(minutes=30),
        id="hourly_data_fetch",
        replace_existing=True
    )
    
    # 日线：每天 02:00 UTC
    scheduler.add_job(
        job_fetch_daily_data,
        CronTrigger(hour=2, minute=0),
        id="daily_data_fetch",
        replace_existing=True
    )

    # 新闻：每1小时
    scheduler.add_job(
        job_fetch_news,
        IntervalTrigger(hours=1),
        id="news_fetch",
        replace_existing=True
    )
    
    # 2. 分析任务
    # 指标 (1m)：每1分钟
    scheduler.add_job(
        job_calculate_indicators_1m,
        IntervalTrigger(minutes=1),
        id="indicator_calculation_1m",
        replace_existing=True
    )
    
    # 指标 (1h)：每1小时
    scheduler.add_job(
        job_calculate_indicators_1h,
        IntervalTrigger(hours=1),
        id="indicator_calculation_1h",
        replace_existing=True
    )

    # 指标 (1d)：每天 02:05 UTC (在日线数据获取后)
    scheduler.add_job(
        job_calculate_indicators_1d,
        CronTrigger(hour=2, minute=5),
        id="indicator_calculation_1d",
        replace_existing=True
    )
    
    # 预测：每4小时
    scheduler.add_job(
        job_generate_forecast,
        IntervalTrigger(hours=4),
        id="forecast_generation",
        replace_existing=True
    )
    
    # 3. 监控任务
    # 告警：每1分钟
    scheduler.add_job(
        job_check_alerts,
        IntervalTrigger(minutes=1),
        id="alert_check",
        replace_existing=True
    )
    
    # 在单独的线程中运行启动任务
    startup_thread = Thread(target=run_startup_jobs, daemon=True)
    startup_thread.start()

    return scheduler

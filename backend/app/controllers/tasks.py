from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.dao.task_dao import TaskDAO
from datetime import timezone

# 创建路由实例
router = APIRouter()

@router.get("/status")
def get_status(db: Session = Depends(get_db)):
    """
    获取系统定时任务的执行状态。
    
    参数:
        db (Session): 数据库会话依赖。
        
    返回:
        dict: 包含各关键任务（如数据采集、指标计算、预测生成等）的执行统计信息。
              包括：上次运行时间、采集数量、总运行次数、错误信息等。
    """
    tasks = TaskDAO().get_all(db)
    task_map = {t.name: t for t in tasks}
    
    # 定义需要监控并返回的目标任务列表
    target_tasks = [
        "realtime_data_fetch",      # 实时数据采集
        "hourly_data_fetch",        # 小时级数据采集
        "daily_data_fetch",         # 日级数据采集
        "news_fetch",               # 新闻资讯采集
        "indicator_calculation_1m", # 分钟级指标计算
        "indicator_calculation_1h", # 小时级指标计算
        "indicator_calculation_1d", # 日级指标计算
        "forecast_generation",      # 预测生成
        "alert_check"               # 告警检查
    ]
    
    out = {}
    for name in target_tasks:
        t = task_map.get(name)
        if t:
            out[name] = {
                "last_run": t.last_run.replace(tzinfo=timezone.utc) if t.last_run else None,
                "inserted": t.inserted,
                "total_runs": t.total_runs,
                "error": t.error,
            }
        else:
            # 如果任务尚未执行过，返回默认空状态
            out[name] = {
                "last_run": None,
                "inserted": 0,
                "total_runs": 0,
                "error": None,
            }
    return out

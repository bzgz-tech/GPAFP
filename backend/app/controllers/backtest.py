from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.backtest import BacktestOut
from app.services_impl.backtest_service_impl import BacktestServiceImpl
from app.dao.backtest_dao import BacktestDAO
from app.core.deps import get_db
from datetime import timezone

# 创建路由实例
router = APIRouter()

@router.get("/latest", response_model=BacktestOut)
def read_latest_backtest(
    strategy: str = "basic",
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    db: Session = Depends(get_db),
):
    """
    获取最新的回测结果。
    
    参数:
        strategy (str): 回测策略名称，默认为 "basic"。
        symbol (str): 交易品种，默认为 "XAUUSD"。
        timeframe (str): 时间周期，默认为 "1d"（日线）。
        db (Session): 数据库会话依赖。
        
    返回:
        BacktestOut: 回测结果详情，包含收益率、最大回撤等指标。
    """
    service = BacktestServiceImpl(BacktestDAO())
    result = service.get_latest_backtest(db, strategy, symbol, timeframe)
    
    # 确保返回的时间戳包含时区信息（UTC）
    if result:
        if result.start_ts and result.start_ts.tzinfo is None:
            result.start_ts = result.start_ts.replace(tzinfo=timezone.utc)
        if result.end_ts and result.end_ts.tzinfo is None:
            result.end_ts = result.end_ts.replace(tzinfo=timezone.utc)
    return result

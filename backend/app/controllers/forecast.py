from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.forecast import ForecastOut, ForecastPointOut
from app.services_impl.forecast_service_impl import ForecastServiceImpl
from app.dao.forecast_dao import ForecastDAO
from app.dao.price_dao import PriceDAO
from app.core.deps import get_db
from datetime import datetime, timedelta, timezone

# 创建路由实例
router = APIRouter()

@router.get("/latest", response_model=ForecastOut)
def read_latest_forecast(
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    horizon: int = 1,
    usd_cny: float = 7.1,
    db: Session = Depends(get_db),
):
    """
    获取最新的价格预测结果，并转换为人民币单位。
    
    参数:
        symbol (str): 交易品种，默认为 "XAUUSD"。
        timeframe (str): 时间周期，默认为 "1d"。
        horizon (int): 预测步长，默认为 1（如下一日）。
        usd_cny (float): 美元兑人民币汇率，默认为 7.1。
        db (Session): 数据库会话依赖。
        
    返回:
        ForecastOut: 预测结果对象，包含预测值及置信区间（已转换为元/克）。
    """
    service = ForecastServiceImpl(ForecastDAO(), PriceDAO())
    result = service.get_latest_forecast(db, symbol, timeframe, horizon)
    
    if result:
        # 换算系数：美元/盎司 -> 人民币/克
        # 1 盎司 ≈ 31.1034768 克
        ratio = usd_cny / 31.1034768
        
        # 确保时间戳包含 UTC 时区信息
        if result.ts.tzinfo is None:
            result.ts = result.ts.replace(tzinfo=timezone.utc)
            
        # 构建并返回转换后的预测结果
        return ForecastOut(
            id=result.id,
            symbol=result.symbol,
            timeframe=result.timeframe,
            ts=result.ts,
            horizon=result.horizon,
            value=round(result.value * ratio, 2), # 预测值
            lower=round(result.lower * ratio, 2) if result.lower is not None else None, # 下界
            upper=round(result.upper * ratio, 2) if result.upper is not None else None, # 上界
        )
    return result

@router.get("/history", response_model=list[ForecastPointOut])
def read_forecast_history(
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    horizon: int = 1,
    window: str = "1m",
    usd_cny: float = 7.1,
    db: Session = Depends(get_db),
):
    """
    获取历史预测记录，用于展示预测准确性走势。
    
    参数:
        symbol (str): 交易品种。
        timeframe (str): 时间周期。
        horizon (int): 预测步长。
        window (str): 历史数据窗口大小（如 "1m" 表示最近一个月）。
        usd_cny (float): 汇率。
        db (Session): 数据库会话。
        
    返回:
        list[ForecastPointOut]: 历史预测点序列（已转换为元/克）。
    """
    now = datetime.utcnow()
    # 窗口大小映射到天数
    days_map = {"1d": 1, "1m": 30, "3m": 90, "1y": 365}
    days = days_map.get(window, 30)
    start_ts = now - timedelta(days=days)
    
    service = ForecastServiceImpl(ForecastDAO(), PriceDAO())
    rows = service.get_history(db, symbol, timeframe, horizon, start_ts)
    
    # 换算系数
    ratio = usd_cny / 31.1034768
    
    # 转换并返回数据列表
    return [
        {
            "ts": r.ts.replace(tzinfo=timezone.utc), 
            "value": round(r.value * ratio, 2), 
            "lower": round(r.lower * ratio, 2) if r.lower is not None else None, 
            "upper": round(r.upper * ratio, 2) if r.upper is not None else None
        } for r in rows
    ]

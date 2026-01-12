from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.market import PriceOut, PricePointOut, PriceDetailedOut
from app.services_impl.market_service_impl import MarketServiceImpl
from app.dao.price_dao import PriceDAO
from app.core.deps import get_db
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

# 创建路由实例
router = APIRouter()

@router.get("/latest", response_model=PriceOut)
def read_latest_price(
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    usd_cny: float = 7.1,
    db: Session = Depends(get_db),
):
    """
    获取最新的市场价格数据，并转换为人民币单位。
    
    参数:
        symbol (str): 交易品种。
        timeframe (str): 时间周期。
        usd_cny (float): 汇率。
        db (Session): 数据库会话。
        
    返回:
        PriceOut: 包含开高低收价格（已换算为元/克）及成交量的对象。
    """
    service = MarketServiceImpl(PriceDAO())
    result = service.get_latest_price(db, symbol, timeframe)
    if result:
        # 确保时区正确
        if result.ts.tzinfo is None:
            result.ts = result.ts.replace(tzinfo=timezone.utc)
        
        # 换算系数：美元/盎司 -> 人民币/克 (仅针对 XAUUSD)
        if symbol == "XAUUSD":
            ratio = usd_cny / 31.1034768
        else:
            ratio = 1.0
            
        return PriceOut(
            id=result.id,
            symbol=result.symbol,
            timeframe=result.timeframe,
            ts=result.ts,
            open=round(result.open * ratio, 2),
            high=round(result.high * ratio, 2),
            low=round(result.low * ratio, 2),
            close=round(result.close * ratio, 2),
            volume=result.volume,
            created_at=result.created_at
        )
    return result

@router.get("/history", response_model=list[PricePointOut])
def read_history(
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    window: str = "1m",
    usd_cny: float = 7.1,
    db: Session = Depends(get_db),
):
    """
    获取简化的历史价格序列（仅包含时间戳和收盘价），适用于绘制走势图。
    
    参数:
        symbol (str): 交易品种。
        timeframe (str): 时间周期。
        window (str): 历史窗口大小。
        usd_cny (float): 汇率。
        db (Session): 数据库会话。
        
    返回:
        list[PricePointOut]: 历史价格点列表。
    """
    now = datetime.utcnow()
    days_map = {"1d": 1, "1m": 30, "3m": 90, "6m": 180, "1y": 365, "5y": 365 * 5}
    days = days_map.get(window, 30)
    start_ts = now - timedelta(days=days)
    
    service = MarketServiceImpl(PriceDAO())
    rows = service.get_history(db, symbol, timeframe, start_ts)
    
    # Check if we need to import data (missing or incomplete)
    should_import = False
    if not rows:
        should_import = True
    elif days > 30: # Check for gaps in longer history
        first_ts = rows[0].ts.replace(tzinfo=None)
        # If data starts significantly later than requested start time (allow 15 days buffer)
        start_gap = (first_ts - start_ts).days > 15
        count_gap = len(rows) < (days * 0.4)
        
        if start_gap or count_gap:
            should_import = True

    # Auto-import if needed
    if should_import:
        try:
            # Determine appropriate window based on timeframe
            import_window = window
            if timeframe == "1m":
                import_window = "5d"
            service.import_history(db, symbol, timeframe, import_window)
            rows = service.get_history(db, symbol, timeframe, start_ts)
        except Exception as e:
             print(f"Auto-import failed: {e}")

    if symbol == "XAUUSD":
        ratio = usd_cny / 31.1034768
    else:
        ratio = 1.0
    return [{"ts": r.ts.replace(tzinfo=timezone.utc), "value": round(r.close * ratio, 2), "created_at": r.created_at} for r in rows]

@router.get("/history/detailed", response_model=list[PriceDetailedOut])
def read_detailed_history(
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    window: str = "1m",
    usd_cny: float = 7.1,
    db: Session = Depends(get_db),
):
    """
    获取详细的历史价格数据（OHLCV），适用于表格展示。
    结果按时间倒序排列（最新的在最前）。
    
    参数:
        symbol (str): 交易品种。
        timeframe (str): 时间周期。
        window (str): 历史窗口大小。
        usd_cny (float): 汇率。
        db (Session): 数据库会话。
        
    返回:
        list[PriceDetailedOut]: 详细历史价格列表。
    """
    now = datetime.utcnow()
    days_map = {"1d": 1, "1m": 30, "3m": 90, "6m": 180, "1y": 365, "5y": 365 * 5}
    days = days_map.get(window, 30)
    start_ts = now - timedelta(days=days)
    
    service = MarketServiceImpl(PriceDAO())
    rows = service.get_history(db, symbol, timeframe, start_ts)
    
    # Check if we need to import data
    should_import = False
    if not rows:
        should_import = True
    elif days > 30:
        first_ts = rows[0].ts.replace(tzinfo=None)
        start_gap = (first_ts - start_ts).days > 15
        count_gap = len(rows) < (days * 0.4)
        if start_gap or count_gap:
            should_import = True

    # Auto-import if needed
    if should_import:
        try:
            # Determine appropriate window based on timeframe
            import_window = window
            if timeframe == "1m":
                import_window = "5d"
            service.import_history(db, symbol, timeframe, import_window)
            rows = service.get_history(db, symbol, timeframe, start_ts)
        except Exception as e:
             print(f"Auto-import failed: {e}")

    # 倒序排列，方便前端表格展示
    rows.reverse()
    
    if symbol == "XAUUSD":
        ratio = usd_cny / 31.1034768
    else:
        ratio = 1.0
    
    result = []
    for r in rows:
        result.append({
            "ts": r.ts.replace(tzinfo=timezone.utc),
            "open": round(r.open * ratio, 2),
            "high": round(r.high * ratio, 2),
            "low": round(r.low * ratio, 2),
            "close": round(r.close * ratio, 2),
            "volume": r.volume,
            "created_at": r.created_at
        })
    return result

@router.post("/import")
def import_history(
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    window: str = "1m",
    db: Session = Depends(get_db),
):
    """
    手动触发历史数据导入任务。
    
    参数:
        symbol (str): 交易品种。
        timeframe (str): 时间周期。
        window (str): 导入数据的时间窗口。
        db (Session): 数据库会话。
        
    返回:
        dict: 包含插入记录数的字典。
        
    异常:
        HTTPException(500): 导入过程中发生错误。
    """
    service = MarketServiceImpl(PriceDAO())
    try:
        count = service.import_history(db, symbol, timeframe, window)
        return {"inserted": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

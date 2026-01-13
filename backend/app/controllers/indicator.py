from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.indicator import IndicatorOut, IndicatorPointOut, IndicatorSummary, IndicatorSummaryItem
from app.services_impl.indicator_service_impl import IndicatorServiceImpl
from app.dao.indicator_dao import IndicatorDAO
from app.dao.price_dao import PriceDAO
from app.core.deps import get_db
from datetime import datetime, timedelta, timezone

# 创建路由实例
router = APIRouter()

@router.get("/latest", response_model=IndicatorOut)
def read_latest_indicator(
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    name: str = "RSI",
    usd_cny: float = 7.1,
    db: Session = Depends(get_db),
):
    """
    获取指定技术指标的最新值。
    
    参数:
        symbol (str): 交易品种。
        timeframe (str): 时间周期。
        name (str): 指标名称（如 RSI, MACD, MA）。
        usd_cny (float): 汇率，用于价格类指标的换算。
        db (Session): 数据库会话。
        
    返回:
        IndicatorOut: 指标数据对象。对于价格类指标（MA, MACD），值会自动转换为元/克。
    """
    service = IndicatorServiceImpl(IndicatorDAO(), PriceDAO())
    result = service.get_latest_indicator(db, symbol, timeframe, name)
    if result:
        # 确保时区正确
        if result.ts.tzinfo is None:
            result.ts = result.ts.replace(tzinfo=timezone.utc)
            
        # 如果是价格相关的指标，需要进行单位换算
        if name in ["MA", "MACD"]:
            ratio = usd_cny / 31.1034768
            return IndicatorOut(
                id=result.id,
                symbol=result.symbol,
                timeframe=result.timeframe,
                name=result.name,
                ts=result.ts,
                value=round(result.value * ratio, 2),
                created_at=result.created_at
            )
    return result

@router.get("/history", response_model=list[IndicatorPointOut])
def read_indicator_history(
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    name: str = "RSI",
    window: str = "1m",
    usd_cny: float = 7.1,
    db: Session = Depends(get_db),
):
    """
    获取技术指标的历史数据序列，用于绘图。
    
    参数:
        symbol (str): 交易品种。
        timeframe (str): 时间周期。
        name (str): 指标名称。
        window (str): 历史窗口大小。
        usd_cny (float): 汇率。
        db (Session): 数据库会话。
        
    返回:
        list[IndicatorPointOut]: 指标历史点序列。价格类指标已换算单位。
    """
    now = datetime.utcnow()
    days_map = {"1d": 1, "7d": 7, "1m": 30, "3m": 90, "1y": 365}
    days = days_map.get(window, 30)
    start_ts = now - timedelta(days=days)
    
    service = IndicatorServiceImpl(IndicatorDAO(), PriceDAO())
    rows = service.get_history(db, symbol, timeframe, name, start_ts)
    
    # 价格类指标换算
    if name in ["MA", "MACD"]:
        ratio = usd_cny / 31.1034768
        return [{"ts": r.ts.replace(tzinfo=timezone.utc), "value": round(r.value * ratio, 2)} for r in rows]
    else:
        return [{"ts": r.ts.replace(tzinfo=timezone.utc), "value": r.value} for r in rows]

@router.get("/summary", response_model=IndicatorSummary)
def read_indicator_summary(
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    usd_cny: float = 7.1,
    db: Session = Depends(get_db),
):
    """
    获取综合技术指标分析摘要，包含 RSI, MACD, MA 的信号解读。
    
    参数:
        symbol (str): 交易品种。
        timeframe (str): 时间周期。
        usd_cny (float): 汇率。
        db (Session): 数据库会话。
        
    返回:
        IndicatorSummary: 包含各指标当前值、交易信号（买入/卖出/中性）及描述性文本的摘要对象。
    """
    service = IndicatorServiceImpl(IndicatorDAO(), PriceDAO())
    price_dao = PriceDAO()
    
    ratio = usd_cny / 31.1034768
    
    # 获取最新价格用于 MA 比较
    latest_price_obj = price_dao.get_latest(db, symbol, timeframe)
    latest_price = (latest_price_obj.close * ratio) if latest_price_obj else 0
    latest_ts = latest_price_obj.ts if latest_price_obj else datetime.utcnow()
    
    items = []
    
    # 分析 RSI 指标
    rsi = service.get_latest_indicator(db, symbol, timeframe, "RSI")
    if rsi:
        val = rsi.value
        if val > 70:
            signal = "sell"
            desc = "超买 (RSI > 70)"
        elif val < 30:
            signal = "buy"
            desc = "超卖 (RSI < 30)"
        else:
            signal = "neutral"
            desc = "中性 (30-70)"
        items.append(IndicatorSummaryItem(name="RSI", value=val, signal=signal, desc=desc, unit=""))
        
    # 分析 MACD 指标
    macd = service.get_latest_indicator(db, symbol, timeframe, "MACD")
    if macd:
        val = macd.value * ratio
        if val > 0:
            signal = "buy"
            desc = "看涨 (MACD > 0)"
        else:
            signal = "sell"
            desc = "看跌 (MACD < 0)"
        items.append(IndicatorSummaryItem(name="MACD", value=val, signal=signal, desc=desc, unit="元/克"))
        
    # 分析 MA 指标
    ma = service.get_latest_indicator(db, symbol, timeframe, "MA")
    if ma:
        val = ma.value * ratio
        if latest_price > val:
            signal = "buy"
            desc = f"看涨 (价格 {latest_price:.2f}元/克 > MA {val:.2f}元/克)"
        else:
            signal = "sell"
            desc = f"看跌 (价格 {latest_price:.2f}元/克 < MA {val:.2f}元/克)"
        items.append(IndicatorSummaryItem(name="MA", value=val, signal=signal, desc=desc, unit="元/克"))

    # 使用最新价格的时间戳作为参考
    ts = latest_ts
         
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    
    return IndicatorSummary(
        symbol=symbol,
        timeframe=timeframe,
        ts=ts,
        items=items
    )

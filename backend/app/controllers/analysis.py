from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.services_impl.ai_analysis_service_impl import AIAnalysisServiceImpl
from app.dao.price_dao import PriceDAO
from app.services_impl.market_service_impl import MarketServiceImpl
from app.dao.indicator_dao import IndicatorDAO
from app.services_impl.indicator_service_impl import IndicatorServiceImpl
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/ai_report")
def get_ai_report(
    symbol: str = "XAUUSD",
    timeframe: str = "1d",
    start_date: str | None = None,
    end_date: str | None = None,
    window: str | None = None,
    db: Session = Depends(get_db)
):
    """
    生成基于当前K线和技术指标的 AI 分析报告。
    """
    # 1. 获取价格数据
    price_dao = PriceDAO()
    market_service = MarketServiceImpl(price_dao)
    
    # 确定时间范围
    days = 60 # Default
    try:
        if start_date:
            start_ts = datetime.fromisoformat(start_date.replace("Z", "+00:00")).replace(tzinfo=None)
        elif window:
            days_map = {"1d": 1, "7d": 7, "1m": 30, "3m": 90, "1y": 365}
            days = days_map.get(window, 60)
            start_ts = datetime.utcnow() - timedelta(days=days)
        else:
            start_ts = datetime.utcnow() - timedelta(days=60)

        if end_date:
            end_ts = datetime.fromisoformat(end_date.replace("Z", "+00:00")).replace(tzinfo=None)
        else:
            end_ts = datetime.utcnow()
            
    except ValueError:
        # Fallback to default if date parsing fails
        end_ts = datetime.utcnow()
        start_ts = end_ts - timedelta(days=60)

    prices = market_service.get_history(db, symbol, timeframe, start_ts, end_ts)
    if not prices:
        # 尝试导入数据
        market_service.import_history(db, symbol, timeframe, "3m")
        prices = market_service.get_history(db, symbol, timeframe, start_ts)
        if not prices:
            raise HTTPException(status_code=404, detail="无法获取价格数据，请稍后重试")
        
    # Format prices to dict list
    price_data = [
        {
            "ts": p.ts.strftime("%Y-%m-%d"),
            "open": p.open,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "volume": p.volume
        }
        for p in prices
    ]

    # 2. 获取常用指标数据 (最新值)
    # 我们关注: MA5, MA20, RSI, MACD
    indicator_dao = IndicatorDAO()
    indicator_service = IndicatorServiceImpl(indicator_dao, price_dao)
    
    indicators = {}
    target_indicators = ["MA_5", "MA_20", "RSI_14", "MACD_12_26_9_DIF", "MACD_12_26_9_DEA"]
    
    for name in target_indicators:
        # Try to fetch latest
        ind_data = indicator_service.get_latest_indicator(db, symbol, timeframe, name)
        if ind_data:
            key_name = name
            if name.startswith("MA_"):
                key_name = name.replace("_", "") # MA5, MA20
            elif name.startswith("RSI_"):
                key_name = "RSI"
            elif "DIF" in name:
                key_name = "MACD_DIF"
            elif "DEA" in name:
                key_name = "MACD_DEA"
            
            indicators[key_name] = ind_data.value

    # 3. 调用 AI 分析
    try:
        # Pass None to init if it doesn't accept arguments, or remove it if it does
        # Based on previous fix, AIAnalysisServiceImpl() takes no args (or has defaults)
        ai_service = AIAnalysisServiceImpl()
        result = ai_service.generate_report(symbol, price_data, indicators)
        
        # Compatibility with frontend: map 'content' to 'report'
        if "content" in result:
            result["report"] = result["content"]
            
        # Add debug info for verification (Optional, can remove later)
        result["debug_info"] = {
            "window_param": window,
            "calculated_start_ts": str(start_ts),
            "days_used": days,
            "price_count": len(price_data)
        }
            
        return result
        
    except Exception as e:
        print(f"AI Generation Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI 分析生成失败: {str(e)}")

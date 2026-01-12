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
    db: Session = Depends(get_db)
):
    """
    生成基于当前K线和技术指标的 AI 分析报告。
    """
    # 1. 获取价格数据 (最近 30 天)
    price_dao = PriceDAO()
    market_service = MarketServiceImpl(price_dao)
    
    # 扩大范围以确保有足够的数据计算指标和分析趋势
    end_ts = datetime.utcnow()
    start_ts = end_ts - timedelta(days=60)
    
    prices = market_service.get_history(db, symbol, timeframe, start_ts)
    if not prices:
        # 尝试导入数据
        market_service.import_history(db, symbol, timeframe, "3m")
        prices = market_service.get_history(db, symbol, timeframe, start_ts)
        if not prices:
            raise HTTPException(status_code=404, detail="无法获取价格数据，请稍后重试")
        
    # Format prices to dict list (Last 10 days for Prompt Context is enough, AI Service handles slicing)
    # AI Service will take care of slicing, we pass recent history.
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
    ai_service = AIAnalysisServiceImpl()
    report = ai_service.generate_report(symbol, price_data, indicators)
    
    return {"report": report}

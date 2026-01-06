from sqlalchemy.orm import Session
from ..services.market_service import MarketService
from ..dao.price_dao import PriceDAO
from ..models.price import Price
from ..importers.yahoo import fetch_prices


class MarketServiceImpl(MarketService):
    """
    市场数据服务实现类，负责价格数据的查询和导入。
    """
    def __init__(self, price_dao: PriceDAO):
        self.price_dao = price_dao

    def get_latest_price(self, db: Session, symbol: str, timeframe: str) -> Price | None:
        """
        获取最新的一条价格记录。
        """
        return self.price_dao.get_latest(db, symbol, timeframe)

    def get_history(self, db: Session, symbol: str, timeframe: str, start_ts, end_ts=None) -> list[Price]:
        """
        获取指定时间范围内的历史价格数据。
        """
        return self.price_dao.get_range(db, symbol, timeframe, start_ts, end_ts)

    def import_history(self, db: Session, symbol: str, timeframe: str, window: str) -> int:
        """
        从外部数据源（如 Yahoo Finance）导入历史数据。
        
        参数:
            window (str): 导入的时间跨度，如 "1mo" (1个月), "1y" (1年)。
            
        返回:
            int: 成功插入的新记录数量。
        """
        # 映射内部时间周期到外部 API 参数
        # Yahoo Finance supports: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "1d": "1d",
            "1w": "1wk",
            "1M": "1mo"
        }
        interval = interval_map.get(timeframe, "1d")
        
        # 自动调整请求的数据范围，避免请求过多或过少
        # 分钟级数据通常只能获取最近的（如 1m 只能最近 7 天）
        final_window = window
        if interval in ["1m"]:
            final_window = "5d" # 1m data is limited to 7 days usually
        elif interval in ["5m", "15m", "30m"]:
            final_window = "1mo" # Intraday data limited to 60 days
        elif interval in ["1h"]:
             final_window = "3mo" # Hourly data limited to 730 days

        # 如果用户显式指定了 window，优先尝试使用（除了分钟级限制）
        if window and window != "auto":
             # 仍需遵守分钟级限制
             if interval == "1m" and window in ["1mo", "3mo", "1y"]:
                 final_window = "5d"
             else:
                 final_window = window
        
        # 调用外部导入器获取原始数据
        raw = fetch_prices(symbol, interval, final_window)
        
        # 获取数据库中已有的最新时间戳，用于去重
        max_ts = self.price_dao.get_max_ts(db, symbol, timeframe)
        rows: list[Price] = []
        
        for r in raw:
            # 跳过已存在的记录
            if max_ts and r["ts"] <= max_ts:
                continue
            rows.append(
                Price(
                    symbol=symbol,
                    timeframe=timeframe,
                    ts=r["ts"],
                    open=r["open"],
                    high=r["high"],
                    low=r["low"],
                    close=r["close"],
                    volume=r["volume"],
                )
            )
        
        # 批量插入新数据
        return self.price_dao.bulk_insert(db, rows)

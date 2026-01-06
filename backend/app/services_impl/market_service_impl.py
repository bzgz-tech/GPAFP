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
        interval = "1d" if timeframe == "1d" else "1h"
        rng_map = {"1d": "1d", "1m": "1mo", "3m": "3mo", "1y": "1y"}
        rng = rng_map.get(window, "1mo")
        
        # 调用外部导入器获取原始数据
        raw = fetch_prices(symbol, interval, rng)
        
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

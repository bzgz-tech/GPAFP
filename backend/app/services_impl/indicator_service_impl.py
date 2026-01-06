from sqlalchemy.orm import Session
from ..services.indicator_service import IndicatorService
from ..dao.indicator_dao import IndicatorDAO
from ..dao.price_dao import PriceDAO
from ..models.indicator import Indicator
import pandas as pd
import numpy as np

class IndicatorServiceImpl(IndicatorService):
    """
    指标服务实现类，负责计算和查询技术指标（如 RSI, MA, MACD）。
    """
    def __init__(self, indicator_dao: IndicatorDAO, price_dao: PriceDAO):
        self.indicator_dao = indicator_dao
        self.price_dao = price_dao

    def get_latest_indicator(self, db: Session, symbol: str, timeframe: str, name: str) -> Indicator | None:
        """
        获取最新指标值。如果不存在，触发计算。
        """
        result = self.indicator_dao.get_latest(db, symbol, timeframe, name)
        if not result:
             self.calculate_and_save(db, symbol, timeframe, name)
             result = self.indicator_dao.get_latest(db, symbol, timeframe, name)
        return result

    def get_history(self, db: Session, symbol: str, timeframe: str, name: str, start_ts, end_ts=None) -> list[Indicator]:
        """
        获取历史指标数据。如果不存在，触发计算。
        """
        rows = self.indicator_dao.get_range(db, symbol, timeframe, name, start_ts, end_ts)
        if not rows:
            self.calculate_and_save(db, symbol, timeframe, name)
            rows = self.indicator_dao.get_range(db, symbol, timeframe, name, start_ts, end_ts)
        return rows

    def calculate_and_save(self, db: Session, symbol: str, timeframe: str, name: str):
        """
        计算并保存技术指标。
        
        支持的指标:
            - RSI: 相对强弱指数 (14周期)
            - MA: 移动平均线 (20周期)
            - MACD: 指数平滑异同移动平均线 (12, 26, 9)
            
        逻辑:
            1. 获取全量历史价格数据。
            2. 使用 Pandas/Numpy 计算指标值。
            3. 清洗数据（去除 NaN）。
            4. 覆盖更新数据库中的指标记录。
        """
        # 获取所有价格数据以确保计算准确
        prices = self.price_dao.get_range(db, symbol, timeframe, start_ts=None)
        if not prices:
            return

        df = pd.DataFrame([{
            "ts": p.ts,
            "close": p.close
        } for p in prices])
        df.sort_values("ts", inplace=True)
        df.set_index("ts", inplace=True)

        # 根据指标名称应用不同的计算逻辑
        if name == "RSI":
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df["value"] = 100 - (100 / (1 + rs))
        elif name == "MA":
            df["value"] = df["close"].rolling(window=20).mean()
        elif name == "MACD":
            exp1 = df["close"].ewm(span=12, adjust=False).mean()
            exp2 = df["close"].ewm(span=26, adjust=False).mean()
            df["value"] = exp1 - exp2
        
        # 准备批量插入
        indicators = []
        
        # 仅保留有效值
        df.dropna(subset=["value"], inplace=True)
        
        for ts, row in df.iterrows():
            indicators.append(Indicator(
                symbol=symbol,
                timeframe=timeframe,
                ts=ts,
                name=name,
                value=float(row["value"])
            ))
            
        if indicators:
            # 简单的去重策略：删除该维度下的所有旧数据并重新插入
            # 在生产环境中，建议使用 upsert 以提高性能
            from sqlalchemy import delete
            stmt = delete(Indicator).where(
                Indicator.symbol == symbol,
                Indicator.timeframe == timeframe,
                Indicator.name == name
            )
            db.execute(stmt)
            db.bulk_save_objects(indicators)
            db.commit()

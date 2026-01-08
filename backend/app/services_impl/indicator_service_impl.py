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
            - RSI: 相对强弱指数 (默认14周期, 可用 RSI_6, RSI_12)
            - MA: 移动平均线 (默认20周期, 可用 MA_5, MA_10, MA_60)
            - MACD: 指数平滑异同移动平均线 (12, 26, 9)
            - KDJ: 随机指标 (9, 3, 3) - 返回 K, D, J 三个值 (存储为 KDJ_K, KDJ_D, KDJ_J)
            - SUPPORT: 支撑位 (默认20周期低点)
            - RESISTANCE: 压力位 (默认20周期高点)
            
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
            "open": p.open,
            "high": p.high,
            "low": p.low,
            "close": p.close
        } for p in prices])
        df.sort_values("ts", inplace=True)
        df.set_index("ts", inplace=True)

        # 解析参数 (例如 MA_5 -> type=MA, period=5)
        parts = name.split('_')
        base_name = parts[0]
        param = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None

        # 根据指标名称应用不同的计算逻辑
        if base_name == "RSI":
            period = param if param else 14
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            df["value"] = 100 - (100 / (1 + rs))
            
        elif base_name == "MA":
            period = param if param else 20
            df["value"] = df["close"].rolling(window=period).mean()
            
        elif base_name == "MACD":
            # MACD 只需要计算 DIFF (快线 - 慢线), DEA, MACD柱
            # 这里简化处理，如果 name 是 MACD，默认返回 DIFF
            # 如果需要 DEA/MACD柱，可以用 MACD_DEA, MACD_HIST
            fast_period = 12
            slow_period = 26
            signal_period = 9
            
            exp1 = df["close"].ewm(span=fast_period, adjust=False).mean()
            exp2 = df["close"].ewm(span=slow_period, adjust=False).mean()
            diff = exp1 - exp2
            dea = diff.ewm(span=signal_period, adjust=False).mean()
            hist = 2 * (diff - dea)
            
            if "DEA" in name:
                df["value"] = dea
            elif "HIST" in name:
                df["value"] = hist
            else:
                df["value"] = diff
                
        elif base_name == "KDJ":
            # Default parameters
            n, m1, m2 = 9, 3, 3
            
            # Try to parse custom parameters from name
            # Expected formats: KDJ_K, KDJ_9_3_3_K
            digits = [int(p) for p in parts if p.isdigit()]
            if len(digits) >= 3:
                n, m1, m2 = digits[0], digits[1], digits[2]

            # KDJ calculation
            low_list = df['low'].rolling(window=n, min_periods=n).min()
            high_list = df['high'].rolling(window=n, min_periods=n).max()
            rsv = (df['close'] - low_list) / (high_list - low_list) * 100
            
            # com = 1 / alpha - 1
            # alpha = 1 / M
            # com = M - 1
            com_k = m1 - 1
            com_d = m2 - 1
            
            k = rsv.ewm(com=com_k, adjust=False).mean()
            d = k.ewm(com=com_d, adjust=False).mean()
            j = 3 * k - 2 * d
            
            if "K" in parts: # Check parts list for component
                df["value"] = k
            elif "D" in parts:
                df["value"] = d
            elif "J" in parts:
                df["value"] = j
            else:
                # Default fallback if ambiguous
                if "K" in name: df["value"] = k
                elif "D" in name: df["value"] = d
                elif "J" in name: df["value"] = j
                else: df["value"] = k

        elif base_name == "SUPPORT":
            period = param if param else 20
            df["value"] = df["low"].rolling(window=period).min()
            
        elif base_name == "RESISTANCE":
            period = param if param else 20
            df["value"] = df["high"].rolling(window=period).max()

        # 准备批量插入
        indicators = []
        
        # 仅保留有效值
        if "value" in df.columns:
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

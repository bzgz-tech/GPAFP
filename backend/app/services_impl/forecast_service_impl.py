from sqlalchemy.orm import Session
from ..services.forecast_service import ForecastService
from ..dao.forecast_dao import ForecastDAO
from ..dao.price_dao import PriceDAO
from ..models.forecast import Forecast
import pandas as pd
import numpy as np
from datetime import timedelta

class ForecastServiceImpl(ForecastService):
    """
    预测服务实现类，负责生成和查询价格预测数据。
    使用指数移动平均 (EMA) 算法进行趋势预测。
    """
    def __init__(self, forecast_dao: ForecastDAO, price_dao: PriceDAO):
        self.forecast_dao = forecast_dao
        self.price_dao = price_dao

    def get_latest_forecast(self, db: Session, symbol: str, timeframe: str, horizon: int) -> Forecast | None:
        """
        获取最新的预测结果。如果发现数据陈旧（基于最新价格），会自动触发重新计算。
        
        参数:
            horizon (int): 预测步长（例如 1 代表预测下一个时间单位）。
        """
        result = self.forecast_dao.get_latest(db, symbol, timeframe, horizon)
        
        # 检查数据新鲜度：我们是否拥有基于最新价格的“下一步”预测？
        latest_price = self.price_dao.get_latest(db, symbol, timeframe)
        need_recalc = False
        
        if not result:
            need_recalc = True
        elif latest_price:
            # 计算预期的预测时间点
            step = timedelta(days=1) if timeframe == "1d" else timedelta(hours=1)
            # 预期时间点 = 最新价格时间 + 预测步长
            expected_ts = latest_price.ts + (step * horizon)
            
            # 如果现有预测的时间早于预期时间（说明有了新的价格数据但未更新预测），则重新计算
            if result.ts < expected_ts:
                need_recalc = True
        
        if need_recalc:
            self.calculate_and_save(db, symbol, timeframe, horizon)
            result = self.forecast_dao.get_latest(db, symbol, timeframe, horizon)
            
        return result

    def get_history(self, db: Session, symbol: str, timeframe: str, horizon: int, start_ts, end_ts=None) -> list[Forecast]:
        """
        获取历史预测记录。如果该时间段无数据，会尝试触发计算。
        """
        rows = self.forecast_dao.get_range(db, symbol, timeframe, horizon, start_ts, end_ts)
        if not rows:
            self.calculate_and_save(db, symbol, timeframe, horizon)
            rows = self.forecast_dao.get_range(db, symbol, timeframe, horizon, start_ts, end_ts)
        return rows

    def calculate_and_save(self, db: Session, symbol: str, timeframe: str, horizon: int):
        """
        核心预测算法：计算并保存预测数据。
        
        算法逻辑:
            1. 获取历史价格数据。
            2. 使用 Pandas 计算 EMA (指数移动平均)，span=5 (对近期价格敏感)。
            3. 将 EMA 向后平移 horizon 个单位作为预测值 (简单的趋势跟随假设)。
            4. 计算上下界 (置信区间)，此处简单设定为 +/- 2%。
            5. 生成未来时刻的预测点。
            6. 全量替换该维度的旧预测数据。
        """
        prices = self.price_dao.get_range(db, symbol, timeframe, start_ts=None)
        if not prices:
            return

        df = pd.DataFrame([{
            "ts": p.ts,
            "close": p.close
        } for p in prices])
        df.sort_values("ts", inplace=True)
        df.set_index("ts", inplace=True)
        
        # 使用 EMA (指数移动平均) 以获得更好的近期响应性
        # span=5 对应 alpha=2/(5+1) = 0.33
        df["ema"] = df["close"].ewm(span=5, adjust=False).mean()
        
        # 将 EMA 向前移动 horizon 步作为预测
        # Forecast[t] = EMA[t-horizon] (意味着我们假设当前趋势会延续)
        df["forecast"] = df["ema"].shift(horizon)
        
        # 添加置信区间 (例如 +/- 2%)
        df["lower"] = df["forecast"] * 0.98
        df["upper"] = df["forecast"] * 1.02
        
        # 获取最后一个 EMA 值，用于生成未来的预测点
        last_val = df["ema"].iloc[-1]
        last_date = df.index[-1]

        # 准备批量插入的数据对象
        forecasts = []
        df.dropna(subset=["forecast"], inplace=True)
        
        for ts, row in df.iterrows():
            forecasts.append(Forecast(
                symbol=symbol,
                timeframe=timeframe,
                ts=ts,
                horizon=horizon,
                value=float(row["forecast"]),
                lower=float(row["lower"]),
                upper=float(row["upper"])
            ))
            
        # 添加未来预测点 (基于当前最新数据预测未来 T+horizon)
        if not pd.isna(last_val):
            future_ts = last_date + timedelta(days=horizon) if timeframe == "1d" else last_date + timedelta(hours=horizon)
            forecasts.append(Forecast(
                symbol=symbol,
                timeframe=timeframe,
                ts=future_ts,
                horizon=horizon,
                value=float(last_val),
                lower=float(last_val * 0.98),
                upper=float(last_val * 1.02)
            ))

        if forecasts:
            # 先删除旧数据（覆盖更新策略）
            from sqlalchemy import delete
            stmt = delete(Forecast).where(
                Forecast.symbol == symbol,
                Forecast.timeframe == timeframe,
                Forecast.horizon == horizon
            )
            db.execute(stmt)
            db.bulk_save_objects(forecasts)
            db.commit()

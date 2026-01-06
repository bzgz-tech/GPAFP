from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from app.services.alert_service import AlertService
from app.dao.alert_dao import AlertDAO
from app.dao.price_dao import PriceDAO
from app.models.alert import Alert

class AlertServiceImpl(AlertService):
    """
    告警服务实现类，负责处理价格告警的创建、查询、删除及触发检查逻辑。
    """
    def __init__(self, alert_dao: AlertDAO, price_dao: PriceDAO = None):
        """
        初始化告警服务。
        
        参数:
            alert_dao (AlertDAO): 告警数据访问对象。
            price_dao (PriceDAO, optional): 价格数据访问对象，用于检查告警触发条件。
        """
        self.alert_dao = alert_dao
        self.price_dao = price_dao

    def get_active_alerts(self, db: Session, symbol: str) -> List[Alert]:
        """
        获取指定品种的当前活跃告警。
        """
        return self.alert_dao.get_active(db, symbol)

    def create_alert(self, db: Session, name: str, symbol: str, condition: str, threshold: float) -> Alert:
        """
        创建一个新的告警。
        
        参数:
            name: 告警名称。
            symbol: 交易品种。
            condition: 触发条件 ('price_above' 或 'price_below')。
            threshold: 触发阈值。
        """
        alert = Alert(
            name=name,
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            active=True,
            created_at=datetime.utcnow()
        )
        return self.alert_dao.create(db, alert)

    def delete_alert(self, db: Session, alert_id: int):
        """
        删除指定ID的告警。
        """
        self.alert_dao.delete(db, alert_id)

    def check_alerts(self, db: Session, symbol: str):
        """
        检查指定品种的所有活跃告警是否触发。
        如果触发，将告警状态设为非活跃，并（在实际应用中）发送通知。
        
        逻辑:
            1. 获取该品种的最新价格（优先取1分钟数据，其次1小时，再次日线）。
            2. 遍历所有活跃告警。
            3. 根据条件（高于/低于）判断是否触发。
            4. 触发后更新状态并记录日志。
        """
        # 如果未注入 price_dao，则临时实例化
        price_dao = self.price_dao or PriceDAO()
        
        # 获取最新价格，按粒度优先级尝试：1m -> 1h -> 1d
        latest = price_dao.get_latest(db, symbol, "1m")
        if not latest:
            latest = price_dao.get_latest(db, symbol, "1h")
        if not latest:
            latest = price_dao.get_latest(db, symbol, "1d")
        
        if not latest:
            return []
            
        current_price = latest.close
        alerts = self.alert_dao.get_active(db, symbol)
        
        triggered_list = []
        for alert in alerts:
            is_triggered = False
            if alert.condition == "price_above" and current_price > alert.threshold:
                is_triggered = True
            elif alert.condition == "price_below" and current_price < alert.threshold:
                is_triggered = True
            
            if is_triggered:
                # 标记告警为已触发（非活跃）
                self.alert_dao.update_status(db, alert.id, False)
                # TODO: 集成邮件或短信通知服务
                print(f"告警触发: {alert.name} - 当前价格 {current_price} 满足条件 {alert.condition} {alert.threshold}")
                triggered_list.append(alert)
        
        return triggered_list

    def initialize_defaults(self, db: Session, symbol: str):
        """
        为指定品种初始化默认告警（如果没有任何活跃告警存在）。
        通常用于演示或新用户引导。
        
        默认创建:
            1. 价格上涨 1%
            2. 价格下跌 1%
            3. 突破下一个百元整数关口
        """
        # 检查是否已有活跃告警
        active_alerts = self.alert_dao.get_active(db, symbol)
        if active_alerts:
            return

        # 获取当前基准价格
        price_dao = self.price_dao or PriceDAO()
        latest = price_dao.get_latest(db, symbol, "1m") or \
                 price_dao.get_latest(db, symbol, "1h") or \
                 price_dao.get_latest(db, symbol, "1d")
        
        base_price = latest.close if latest else 2600.0
        
        # 创建默认告警
        # 1. 价格上涨预警 (+1%)
        self.create_alert(
            db, 
            name=f"价格上涨预警 (>{int(base_price * 1.01)})", 
            symbol=symbol, 
            condition="price_above", 
            threshold=round(base_price * 1.01, 2)
        )
        
        # 2. 价格下跌预警 (-1%)
        self.create_alert(
            db, 
            name=f"价格下跌预警 (<{int(base_price * 0.99)})", 
            symbol=symbol, 
            condition="price_below", 
            threshold=round(base_price * 0.99, 2)
        )
        
        # 3. 整数关口突破预警 (下一个百元位)
        next_hundred = (int(base_price) // 100 + 1) * 100
        self.create_alert(
            db, 
            name=f"突破整数关口 ({next_hundred})", 
            symbol=symbol, 
            condition="price_above", 
            threshold=float(next_hundred)
        )

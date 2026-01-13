from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.alert import AlertOut, AlertCreate
from app.services_impl.alert_service_impl import AlertServiceImpl
from app.dao.alert_dao import AlertDAO
from app.core.deps import get_db
from app.schemas.pagination import Page

# 创建路由实例
router = APIRouter()

@router.get("/active", response_model=Page[AlertOut])
def read_active_alerts(
    page: int = 1,
    page_size: int = 20,
    symbol: str = "XAUUSD",
    db: Session = Depends(get_db),
):
    """
    获取当前活跃的告警列表。
    
    参数:
        symbol (str): 交易品种，默认为 "XAUUSD"。
        db (Session): 数据库会话依赖。
        
    返回:
        Page[AlertOut]: 活跃告警列表分页。
    """
    service = AlertServiceImpl(AlertDAO())
    skip = (page - 1) * page_size
    alerts, total = service.get_active_alerts(db, symbol, skip=skip, limit=page_size)
    return Page(
        total=total,
        items=alerts,
        page=page,
        page_size=page_size
    )

@router.post("/", response_model=AlertOut)
def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
):
    """
    创建一个新的价格告警。
    
    参数:
        alert (AlertCreate): 告警创建请求对象，包含名称、品种、条件和阈值。
        db (Session): 数据库会话依赖。
        
    返回:
        AlertOut: 创建成功的告警对象。
    """
    service = AlertServiceImpl(AlertDAO())
    return service.create_alert(db, alert.name, alert.symbol, alert.condition, alert.threshold)

@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
):
    """
    根据ID删除告警。
    
    参数:
        alert_id (int): 要删除的告警ID。
        db (Session): 数据库会话依赖。
        
    返回:
        dict: 操作状态信息。
    """
    service = AlertServiceImpl(AlertDAO())
    service.delete_alert(db, alert_id)
    return {"status": "ok"}

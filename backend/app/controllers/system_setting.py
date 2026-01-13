from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.system_setting import SystemSetting, SystemSettingCreate
from app.services.system_setting_service import SystemSettingService
from app.services_impl.system_setting_service_impl import SystemSettingServiceImpl

router = APIRouter()

def get_service() -> SystemSettingService:
    return SystemSettingServiceImpl()

@router.get("/", response_model=List[SystemSetting])
def get_all_settings(service: SystemSettingService = Depends(get_service)):
    return service.get_all_settings()

@router.get("/{key}", response_model=SystemSetting)
def get_setting(key: str, service: SystemSettingService = Depends(get_service)):
    setting = service.get_setting(key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.post("/", response_model=SystemSetting)
def save_setting(setting: SystemSettingCreate, service: SystemSettingService = Depends(get_service)):
    return service.save_setting(setting)

@router.get("/config/ai_status", response_model=dict)
def check_ai_config_status(service: SystemSettingService = Depends(get_service)):
    """
    Check if AI config is valid/complete
    """
    config = service.get_ai_config()
    # Basic check: needs api_key and provider/model
    missing = []
    if not config.get('ai_api_key'):
        missing.append('ai_api_key')
    if not config.get('ai_provider'):
        missing.append('ai_provider')
        
    return {
        "configured": len(missing) == 0,
        "missing": missing,
        "provider": config.get('ai_provider'),
        "model": config.get('ai_model')
    }

@router.post("/config/test_connection")
def test_connection(config: dict, service: SystemSettingService = Depends(get_service)):
    return service.test_llm_connection(config)

@router.post("/config/test_notification")
def test_notification(config: dict, service: SystemSettingService = Depends(get_service)):
    """
    测试通知发送
    """
    # 临时保存或直接使用传入的 config 来测试？
    # 这里我们直接使用 DB 中的配置，因为前端会先保存再测试。
    # 或者为了方便，如果前端传了 config，我们也可以尝试使用。
    # 但我们的 send_notification 目前只从 DB 读。
    # 让我们假设前端已经保存了。
    
    # 为了更好的体验，如果前端传了 token，我们可以临时使用它。
    # 但 service.send_notification 是从 DB 读取的。
    # 我们先简单实现：先保存，再测试。
    
    success = service.send_notification("系统通知测试", "这是一条测试消息，如果您收到此消息，说明通知配置成功。")
    return {"success": success}

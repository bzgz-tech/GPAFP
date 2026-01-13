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

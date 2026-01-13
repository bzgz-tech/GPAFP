from typing import List, Optional
from sqlalchemy.orm import Session
from app.services.system_setting_service import SystemSettingService
from app.dao.system_setting_dao import SystemSettingDAO
from app.schemas.system_setting import SystemSetting, SystemSettingCreate
from app.core.db import SessionLocal

class SystemSettingServiceImpl(SystemSettingService):
    def __init__(self):
        self.dao = SystemSettingDAO()

    def get_setting(self, key: str) -> Optional[SystemSetting]:
        with SessionLocal() as db:
            return self.dao.get_by_key(db, key)

    def get_all_settings(self) -> List[SystemSetting]:
        with SessionLocal() as db:
            return self.dao.get_all(db)

    def save_setting(self, setting: SystemSettingCreate) -> SystemSetting:
        with SessionLocal() as db:
            return self.dao.create_or_update(db, setting)
            
    def get_ai_config(self) -> dict:
        """
        Helper to get all AI related config as a dict
        """
        config = {}
        with SessionLocal() as db:
            # List of AI related keys
            keys = ['ai_provider', 'ai_model', 'ai_api_key', 'ai_base_url', 'ai_chat_path']
            for key in keys:
                setting = self.dao.get_by_key(db, key)
                if setting and setting.value:
                    config[key] = setting.value
        return config

    def test_llm_connection(self, config: dict) -> dict:
        import requests
        
        api_key = config.get('ai_api_key')
        base_url = config.get('ai_base_url', '').rstrip('/')
        chat_path = config.get('ai_chat_path', 'chat/completions').lstrip('/')
        model = config.get('ai_model')
        
        if not api_key or not base_url or not model:
            return {"success": False, "message": "Missing required configuration"}
            
        url = f"{base_url}/{chat_path}"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                return {"success": True, "message": "Connection successful"}
            else:
                return {"success": False, "message": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)}"}

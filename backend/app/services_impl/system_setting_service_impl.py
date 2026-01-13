from typing import List, Optional
from sqlalchemy.orm import Session
from app.services.system_setting_service import SystemSettingService
from app.dao.system_setting_dao import SystemSettingDAO
from app.schemas.system_setting import SystemSetting, SystemSettingCreate
from app.core.db import SessionLocal
import requests
import json

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
            
    def get_settings(self) -> dict:
        with SessionLocal() as db:
            settings_list = self.dao.get_all(db)
            return {item.key: item.value for item in settings_list}

    def get_ai_config(self) -> dict:
        settings = self.get_settings()
        return {
            'ai_provider': settings.get('ai_provider'),
            'ai_api_key': settings.get('ai_api_key'),
            'ai_base_url': settings.get('ai_base_url'),
            'ai_model': settings.get('ai_model'),
            'ai_chat_path': settings.get('ai_chat_path'),
        }

    def send_notification(self, title: str, content: str) -> bool:
        settings = self.get_settings()
        notify_type = settings.get('notification_type', 'pushplus')
        token = settings.get('notification_token')
        
        if not token:
            return False
            
        try:
            if notify_type == 'pushplus':
                url = 'http://www.pushplus.plus/send'
                data = {
                    "token": token,
                    "title": title,
                    "content": content,
                    "template": "html"
                }
                resp = requests.post(url, json=data, timeout=10)
                return resp.status_code == 200 and resp.json().get('code') == 200
            elif notify_type == 'wechat_work': # 企业微信 Webhook
                url = token # Token 字段直接填完整 Webhook URL
                data = {
                    "msgtype": "text",
                    "text": {
                        "content": f"【{title}】\n{content}"
                    }
                }
                resp = requests.post(url, json=data, timeout=10)
                return resp.status_code == 200 and resp.json().get('errcode') == 0
            
            return False
        except Exception as e:
            print(f"Notification failed: {e}")
            return False

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

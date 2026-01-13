from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.system_setting import SystemSetting, SystemSettingCreate, SystemSettingUpdate

class SystemSettingService(ABC):
    @abstractmethod
    def get_setting(self, key: str) -> Optional[SystemSetting]:
        pass

    @abstractmethod
    def get_all_settings(self) -> List[SystemSetting]:
        pass

    @abstractmethod
    def save_setting(self, setting: SystemSettingCreate) -> SystemSetting:
        pass
        
    @abstractmethod
    def get_ai_config(self) -> dict:
        pass

    @abstractmethod
    def test_llm_connection(self, config: dict) -> dict:
        pass

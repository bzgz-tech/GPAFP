from sqlalchemy.orm import Session
from app.models.system_setting import SystemSetting
from app.schemas.system_setting import SystemSettingCreate, SystemSettingUpdate
from datetime import datetime

class SystemSettingDAO:
    def get_by_key(self, db: Session, key: str):
        return db.query(SystemSetting).filter(SystemSetting.key == key).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(SystemSetting).offset(skip).limit(limit).all()

    def create(self, db: Session, setting: SystemSettingCreate):
        db_setting = SystemSetting(
            key=setting.key,
            value=setting.value,
            description=setting.description,
            updated_at=datetime.now()
        )
        db.add(db_setting)
        db.commit()
        db.refresh(db_setting)
        return db_setting

    def update(self, db: Session, db_setting: SystemSetting, setting: SystemSettingUpdate):
        if setting.value is not None:
            db_setting.value = setting.value
        if setting.description is not None:
            db_setting.description = setting.description
        db_setting.updated_at = datetime.now()
        db.commit()
        db.refresh(db_setting)
        return db_setting
        
    def create_or_update(self, db: Session, setting: SystemSettingCreate):
        existing = self.get_by_key(db, setting.key)
        if existing:
            update_data = SystemSettingUpdate(value=setting.value, description=setting.description)
            return self.update(db, existing, update_data)
        return self.create(db, setting)

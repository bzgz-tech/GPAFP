from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.user import User


class UserDAO:
    def find_by_username(self, db: Session, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return db.execute(stmt).scalar_one_or_none()

    def create(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        return db.query(User).count()

    def get_by_id(self, db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def update_status(self, db: Session, user: User, is_active: bool) -> User:
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        return user

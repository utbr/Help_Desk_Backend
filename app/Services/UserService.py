from sqlalchemy.orm import Session
from app.Database.models import User

class UserService:

    @staticmethod
    def create_user(db: Session, full_name: str, email: str, password_hash: str, role: str = "user"):
        new_user = User(full_name=full_name, email=email, password_hash=password_hash, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def list_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def update_user(db: Session, user_id: int, full_name: str = None, role: str = None, is_active: bool = None):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if full_name:
            user.full_name = full_name
        if role:
            user.role = role
        if is_active is not None:
            user.is_active = is_active
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        db.delete(user)
        db.commit()
        return True

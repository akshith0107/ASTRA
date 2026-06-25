from sqlalchemy.orm import Session
from app.database.models import User
from app.schemas.auth import UserCreate
from app.services.auth_service import get_password_hash

class UserRepository:
    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()
        
    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create(db: Session, user_in: UserCreate, role: str = "analyst") -> User:
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=hashed_password,
            role=role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

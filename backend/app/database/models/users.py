from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.models.base import Base, BaseMixin

class User(Base, BaseMixin):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="analyst")
    
    reports = relationship("Report", back_populates="analyst", cascade="all, delete-orphan")
    settings = relationship("Settings", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Settings(Base, BaseMixin):
    __tablename__ = "settings"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    alert_threshold = Column(Float, default=80.0)
    sound_alerts = Column(Integer, default=1) # 1=True, 0=False
    auto_save = Column(Integer, default=1)
    language = Column(String, default="en")

    user = relationship("User", back_populates="settings")

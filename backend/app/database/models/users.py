from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from app.database.models.base import Base, BaseMixin

class User(Base, BaseMixin):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="analyst")
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    
    reports = relationship("Report", back_populates="analyst", cascade="all, delete-orphan")
    settings = relationship("Settings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class Settings(Base, BaseMixin):
    __tablename__ = "settings"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    alert_threshold = Column(Float, default=80.0)
    sound_alerts = Column(Integer, default=1) # 1=True, 0=False
    auto_save = Column(Integer, default=1)
    language = Column(String, default="en")
    
    whisper_language = Column(String, default="en")
    min_confidence = Column(Float, default=0.40)
    threat_threshold = Column(Float, default=0.70)
    risk_threshold = Column(Float, default=0.50)
    rag_similarity_threshold = Column(Float, default=0.60)
    auto_save_reports = Column(Integer, default=1)
    auto_export = Column(Integer, default=0)
    realtime_notifications = Column(Integer, default=1)

    user = relationship("User", back_populates="settings")

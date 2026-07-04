from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database.models.base import Base, BaseMixin

class RefreshToken(Base, BaseMixin):
    __tablename__ = "refresh_tokens"

    token_hash = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked = Column(Boolean, default=False, nullable=False)
    replaced_by = Column(String, nullable=True)  # Hash of the token that replaced this one during rotation
    client_ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    user = relationship("User", back_populates="refresh_tokens")

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.models.base import Base, BaseMixin

class Alert(Base, BaseMixin):
    __tablename__ = "alerts"

    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"))
    title = Column(String)
    description = Column(String)
    severity = Column(String)
    
    report = relationship("Report", back_populates="alerts")

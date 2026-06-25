from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.models.base import Base, BaseMixin

class Campaign(Base, BaseMixin):
    __tablename__ = "campaigns"

    campaign_name = Column(String, unique=True, index=True)
    scam_type = Column(String)
    threat_level = Column(String)
    report_count = Column(Integer, default=0)
    
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    status = Column(String, default="active")
    description = Column(String)
    
    report_links = relationship("CampaignReport", back_populates="campaign", cascade="all, delete-orphan")

class CampaignReport(Base, BaseMixin):
    __tablename__ = "campaign_reports"

    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"))
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"))
    
    campaign = relationship("Campaign", back_populates="report_links")
    report = relationship("Report", back_populates="campaign_links")

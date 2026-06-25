from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database.models import Campaign, CampaignReport

class CampaignRepository:
    @staticmethod
    def get_total_count(db: Session) -> int:
        return db.query(func.count(Campaign.id)).scalar() or 0
        
    @staticmethod
    def get_top_active(db: Session, limit: int = 5) -> List[Campaign]:
        return db.query(Campaign).order_by(Campaign.report_count.desc()).limit(limit).all()

    @staticmethod
    def get_by_name(db: Session, campaign_name: str) -> Campaign | None:
        return db.query(Campaign).filter(Campaign.campaign_name == campaign_name).first()
        
    @staticmethod
    def create(db: Session, campaign_name: str, threat_level: str) -> Campaign:
        campaign = Campaign(campaign_name=campaign_name, threat_level=threat_level, report_count=1)
        db.add(campaign)
        db.flush()
        return campaign
        
    @staticmethod
    def increment_nodes(db: Session, campaign: Campaign):
        campaign.report_count += 1
        db.flush()
        
    @staticmethod
    def link_report(db: Session, report_id: int, campaign_id: int, similarity_score: float):
        campaign_report = CampaignReport(
            report_id=report_id,
            campaign_id=campaign_id,
            similarity_score=similarity_score
        )
        db.add(campaign_report)
        db.flush()

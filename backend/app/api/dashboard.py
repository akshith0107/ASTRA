import logging
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.repositories.report_repository import ReportRepository
from app.repositories.campaign_repository import CampaignRepository
from app.database.models import Report, User
from app.services.report_export_service import report_export_service
from app.services.llm_service import llm_service
from app.services.audit_logger import audit_logger
from app.services.auth_service import get_current_user
from app.core.limiter import limiter
from cachetools import TTLCache
from fastapi import Request

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory cache for 60 seconds, max 100 items
cache_store = TTLCache(maxsize=100, ttl=60)

@router.get("/dashboard/stats")
@limiter.limit("60/minute")
async def get_dashboard_stats(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns aggregate statistics and threat intelligence trends for the dashboard UI.
    """
    cache_key = "dashboard_stats"
    if cache_key in cache_store:
        return cache_store[cache_key]

    total_reports = ReportRepository.get_total_count(db)
    active_campaigns = CampaignRepository.get_total_count(db)
    critical_alerts = ReportRepository.get_critical_alert_count(db)
    
    # Detection rate
    high_threat_reports = ReportRepository.get_high_threat_count(db)
    detection_rate = round((high_threat_reports / total_reports * 100), 2) if total_reports > 0 else 0.0

    # Threat Distribution (Top Scam Types)
    reports = ReportRepository.get_recent(db, limit=100)
    distribution = {}
    trends = {}
    
    for r in reports:
        # Scam Type distribution
        st = r.scam_type or "Unknown"
        distribution[st] = distribution.get(st, 0) + 1
        
        # Timeline Trends (last 7 days by date string)
        if r.created_at:
            date_str = r.created_at.strftime("%Y-%m-%d")
            trends[date_str] = trends.get(date_str, 0) + 1
            
    # Sort trends chronologically
    sorted_trends = [{"date": k, "count": v} for k, v in sorted(trends.items())]
    sorted_distribution = [{"name": k, "value": v} for k, v in sorted(distribution.items(), key=lambda item: item[1], reverse=True)]

    result = {
        "total_reports": total_reports,
        "active_campaigns": active_campaigns,
        "critical_alerts": critical_alerts,
        "detection_rate": f"{detection_rate}%",
        "threat_distribution": sorted_distribution[:5],
        "timeline_trends": sorted_trends[-7:]
    }
    cache_store[cache_key] = result
    return result

@router.get("/dashboard/campaigns")
@limiter.limit("60/minute")
async def get_dashboard_campaigns(request: Request, db: Session = Depends(get_db), limit: int = 5, current_user: User = Depends(get_current_user)):
    """
    Returns a list of the most active threat campaigns.
    """
    cache_key = f"dashboard_campaigns_{limit}"
    if cache_key in cache_store:
        return cache_store[cache_key]
        
    campaigns = CampaignRepository.get_top_active(db, limit)
    result = [{"id": c.id, "name": c.campaign_name, "threat_level": c.threat_level, "active_nodes": c.report_count} for c in campaigns]
    cache_store[cache_key] = result
    return result

@router.get("/dashboard/reports")
@limiter.limit("60/minute")
async def get_dashboard_reports(request: Request, db: Session = Depends(get_db), limit: int = 10, current_user: User = Depends(get_current_user)):
    """
    Returns a list of recent reports.
    """
    reports = ReportRepository.get_recent(db, limit)
    return [
        {
            "id": r.id, 
            "created_at": r.created_at, 
            "scam_type": r.scam_type, 
            "risk_score": r.risk_score, 
            "risk_level": r.risk_level
        } 
        for r in reports
    ]

@router.get("/reports/{report_id}/export")
@limiter.limit("60/minute")
async def export_report_pdf(request: Request, report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Generates and returns a PDF report for a given analysis.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    audit_logger.log_action(db, f"Report {report_id} Exported")
        
    # Generate LLM Insights
    indicators_list = [i.type for i in report.indicators] if hasattr(report, 'indicators') and report.indicators else []
    threat_summary = await llm_service.generate_threat_summary(
        transcript=report.text_content,
        scam_type=report.scam_type,
        indicators=indicators_list
    )
    
    recommendations = await llm_service.generate_user_recommendations(report.scam_type)
    
    try:
        pdf_bytes = report_export_service.generate_pdf(report, threat_summary, recommendations)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=sentinelx_report_{report_id}.pdf"}
        )
    except Exception as e:
        logger.error(f"Failed to export PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

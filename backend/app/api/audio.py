import logging
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.analysis import AnalyzeResponse, SimilarScam
from app.services.risk_engine import risk_engine
from app.services.indicator_service import indicator_service
from app.database.database import get_db, SessionLocal
from app.database.models import Alert
from app.repositories.report_repository import ReportRepository
from app.services.audit_logger import audit_logger
from app.services.auth_service import get_current_user
from app.database.models import User

from app.core.limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_AUDIO_EXTENSIONS = {"wav", "mp3", "m4a", "ogg"}
MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

async def process_threat_intel_background(
    report_id: int, 
    transcript: str, 
    risk_score: float, 
    risk_level: str, 
    scam_type: str, 
    indicators: list
):
    """
    Background task to handle heavy threat intel operations without blocking the UI.
    """
    logger.info(f"Starting background threat intel for report {report_id}")
    with SessionLocal() as db:
        try:
            from app.services.entity_extractor import entity_extractor
            from app.services.network_service import network_service
            from app.database.models.threat_events import ThreatEvent
            from app.services.campaign_service import campaign_service
            
            extracted_entities = entity_extractor.extract_all(transcript)
            
            # Threat Intelligence: Campaign Management
            campaign = await campaign_service.process_report(
                db, 
                report_id=report_id, 
                transcript=transcript, 
                risk_level=risk_level, 
                scam_type=scam_type
            )
            
            # Link entities to graph
            network_service.process_entities(
                db, 
                entities=extracted_entities, 
                report_id=report_id, 
                risk_score=risk_score,
                campaign_id=campaign.id if campaign else None
            )
            
            # Log threat events
            for ind in indicators:
                event = ThreatEvent(
                    report_id=report_id,
                    event_type=f"{ind['type']} Detected",
                    description=ind['description']
                )
                db.add(event)
                
            db.commit()
            logger.info(f"Completed background threat intel for report {report_id}")
        except Exception as e:
            logger.error(f"Background threat intel failed: {e}")
            db.rollback()

@router.post("/analyze/audio", response_model=AnalyzeResponse)
@limiter.limit("10/minute")
async def analyze_audio(
    request: Request, 
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyzes an audio file for scam patterns orchestrating Whisper, BERT, Heuristics, and RAG.
    Post-processing graph data is deferred to a background task.
    """
    logger.info(f"Received audio analysis request: {file.filename} from {current_user.username}")
    
    # 1. Audio Security Validation
    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ""
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format. Allowed formats: {ALLOWED_AUDIO_EXTENSIONS}")
        
    audio_data = await file.read()
    if len(audio_data) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Audio file too large. Maximum size is 25MB.")
    
    # Audit log
    audit_logger.log_action(db, "Audio Analysis Performed", user_id=current_user.id)
    
    try:
        # Pull ML Services from App State
        whisper_service = request.app.state.whisper_service
        bert_service = request.app.state.bert_service
        rag_service = request.app.state.rag_service
        
        # Step 1: Whisper Transcription and Language Detection
        transcript = await whisper_service.transcribe(audio_data)
        language = await whisper_service.detect_language(audio_data)
        
        # Step 2: BERT Classification
        scam_type, confidence = await bert_service.classify(transcript)
        
        # Step 3: Extract Indicators
        indicators = indicator_service.extract_indicators(transcript)
        
        # Step 4: RAG Threat Intelligence Search
        campaign_name, similarity_score, rag_scam_type = rag_service.retrieve_similar_scams(transcript)
        
        # Step 5: Calculate Risk Score
        risk_score, risk_level = risk_engine.calculate_risk(
            base_confidence=confidence if scam_type != "Legitimate" else 0.0,
            indicators=indicators,
            similar_scam_score=similarity_score
        )
        
        # If RAG is highly confident, override generic BERT scam type
        final_scam_type = scam_type
        if similarity_score > 0.85 and rag_scam_type:
            final_scam_type = rag_scam_type
            
        similar_scams = []
        if campaign_name:
            similar_scams.append(
                SimilarScam(
                    campaign_name=campaign_name, 
                    similarity_score=similarity_score, 
                    scam_type=rag_scam_type or "Unknown"
                )
            )

        # Build Response
        response_data = AnalyzeResponse(
            risk_score=risk_score,
            risk_level=risk_level,
            scam_type=final_scam_type,
            confidence=max(confidence, similarity_score),
            indicators=indicators,
            transcript=transcript,
            language=language,
            similar_scams=similar_scams
        )
        
        # Step 6: Database Storage via Repository
        db_report = ReportRepository.create(
            db, 
            text_content=transcript,
            risk_score=risk_score,
            risk_level=risk_level,
            scam_type=final_scam_type,
            confidence=max(confidence, similarity_score),
            indicators=[ind.model_dump() for ind in indicators]
        )
        
        if risk_level in ["HIGH_RISK", "CRITICAL"]:
            alert = Alert(
                report_id=db_report.id,
                threat_level=risk_level,
                message=f"Critical Threat Detected: {final_scam_type}"
            )
            db.add(alert)
            db.commit()
            
        # Step 7: Offload Threat Intel post-processing to BackgroundTask
        # NOTE: Do not pass 'db' session to background task.
        background_tasks.add_task(
            process_threat_intel_background,
            db_report.id,
            transcript,
            risk_score,
            risk_level,
            final_scam_type,
            [ind.model_dump() for ind in indicators]
        )
            
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during audio analysis: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during audio analysis")

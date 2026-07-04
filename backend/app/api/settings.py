import logging
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database.database import get_db
from app.database.models import User, Settings, RefreshToken
from app.services.auth_service import get_current_user, get_password_hash, verify_password
from app.core.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Schemas
class SettingsResponse(BaseModel):
    alert_threshold: float
    sound_alerts: bool
    auto_save: bool
    language: str
    whisper_language: str
    min_confidence: float
    threat_threshold: float
    risk_threshold: float
    rag_similarity_threshold: float
    auto_save_reports: bool
    auto_export: bool
    realtime_notifications: bool

    class Config:
        from_attributes = True

class SettingsUpdateRequest(BaseModel):
    alert_threshold: Optional[float] = None
    sound_alerts: Optional[bool] = None
    auto_save: Optional[bool] = None
    language: Optional[str] = None
    whisper_language: Optional[str] = None
    min_confidence: Optional[float] = None
    threat_threshold: Optional[float] = None
    risk_threshold: Optional[float] = None
    rag_similarity_threshold: Optional[float] = None
    auto_save_reports: Optional[bool] = None
    auto_export: Optional[bool] = None
    realtime_notifications: Optional[bool] = None

class ProfileResponse(BaseModel):
    username: str
    email: str
    role: str
    created_at: str

class ProfileUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# Helper to get or create settings
def get_user_settings(db: Session, user_id: int) -> Settings:
    settings_obj = db.query(Settings).filter(Settings.user_id == user_id).first()
    if not settings_obj:
        settings_obj = Settings(user_id=user_id)
        db.add(settings_obj)
        db.commit()
        db.refresh(settings_obj)
    return settings_obj

@router.get("/settings/me", response_model=SettingsResponse)
@limiter.limit("60/minute")
async def get_settings(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings_obj = get_user_settings(db, current_user.id)
    return SettingsResponse(
        alert_threshold=settings_obj.alert_threshold,
        sound_alerts=bool(settings_obj.sound_alerts),
        auto_save=bool(settings_obj.auto_save),
        language=settings_obj.language or "en",
        whisper_language=settings_obj.whisper_language or "en",
        min_confidence=settings_obj.min_confidence or 0.40,
        threat_threshold=settings_obj.threat_threshold or 0.70,
        risk_threshold=settings_obj.risk_threshold or 0.50,
        rag_similarity_threshold=settings_obj.rag_similarity_threshold or 0.60,
        auto_save_reports=bool(settings_obj.auto_save_reports),
        auto_export=bool(settings_obj.auto_export),
        realtime_notifications=bool(settings_obj.realtime_notifications)
    )

@router.put("/settings/me", response_model=SettingsResponse)
@limiter.limit("30/minute")
async def update_settings(
    request: Request,
    body: SettingsUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings_obj = get_user_settings(db, current_user.id)
    
    # Update properties
    if body.alert_threshold is not None:
        settings_obj.alert_threshold = body.alert_threshold
    if body.sound_alerts is not None:
        settings_obj.sound_alerts = 1 if body.sound_alerts else 0
    if body.auto_save is not None:
        settings_obj.auto_save = 1 if body.auto_save else 0
    if body.language is not None:
        settings_obj.language = body.language
    if body.whisper_language is not None:
        settings_obj.whisper_language = body.whisper_language
    if body.min_confidence is not None:
        settings_obj.min_confidence = body.min_confidence
    if body.threat_threshold is not None:
        settings_obj.threat_threshold = body.threat_threshold
    if body.risk_threshold is not None:
        settings_obj.risk_threshold = body.risk_threshold
    if body.rag_similarity_threshold is not None:
        settings_obj.rag_similarity_threshold = body.rag_similarity_threshold
    if body.auto_save_reports is not None:
        settings_obj.auto_save_reports = 1 if body.auto_save_reports else 0
    if body.auto_export is not None:
        settings_obj.auto_export = 1 if body.auto_export else 0
    if body.realtime_notifications is not None:
        settings_obj.realtime_notifications = 1 if body.realtime_notifications else 0

    db.commit()
    db.refresh(settings_obj)
    
    return SettingsResponse(
        alert_threshold=settings_obj.alert_threshold,
        sound_alerts=bool(settings_obj.sound_alerts),
        auto_save=bool(settings_obj.auto_save),
        language=settings_obj.language or "en",
        whisper_language=settings_obj.whisper_language or "en",
        min_confidence=settings_obj.min_confidence or 0.40,
        threat_threshold=settings_obj.threat_threshold or 0.70,
        risk_threshold=settings_obj.risk_threshold or 0.50,
        rag_similarity_threshold=settings_obj.rag_similarity_threshold or 0.60,
        auto_save_reports=bool(settings_obj.auto_save_reports),
        auto_export=bool(settings_obj.auto_export),
        realtime_notifications=bool(settings_obj.realtime_notifications)
    )

@router.get("/settings/profile", response_model=ProfileResponse)
@limiter.limit("60/minute")
async def get_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    created_str = current_user.created_at.strftime("%Y-%m-%d") if current_user.created_at else "Unknown"
    return ProfileResponse(
        username=current_user.username,
        email=current_user.email,
        role=current_user.role or "analyst",
        created_at=created_str
    )

@router.put("/settings/profile", response_model=ProfileResponse)
@limiter.limit("30/minute")
async def update_profile(
    request: Request,
    body: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    if body.username:
        # Check if username is taken
        existing = db.query(User).filter(User.username == body.username, User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken.")
        user.username = body.username
    if body.email:
        # Check if email is taken
        existing = db.query(User).filter(User.email == body.email, User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered.")
        user.email = body.email

    db.commit()
    db.refresh(user)
    
    created_str = user.created_at.strftime("%Y-%m-%d") if user.created_at else "Unknown"
    return ProfileResponse(
        username=user.username,
        email=user.email,
        role=user.role or "analyst",
        created_at=created_str
    )

@router.post("/settings/change-password")
@limiter.limit("10/minute")
async def change_password(
    request: Request,
    body: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password.")
    
    user.password_hash = get_password_hash(body.new_password)
    db.commit()
    return {"message": "Password updated successfully."}

@router.post("/settings/logout-all")
@limiter.limit("10/minute")
async def logout_all_devices(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revokes all active refresh tokens for the current operator."""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False
    ).update({RefreshToken.revoked: True})
    db.commit()
    return {"message": "Logged out from all active sessions successfully."}

@router.delete("/settings/delete-account")
@limiter.limit("5/minute")
async def delete_account(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes operator account permanently."""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    db.delete(user)
    db.commit()
    return {"message": "Account deleted successfully."}

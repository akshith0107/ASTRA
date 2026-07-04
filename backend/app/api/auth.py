import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, Settings, RefreshToken
from app.core.config import settings
from app.services.auth_service import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    hash_token,
    revoke_token_from_cache,
    get_current_user
)
from app.schemas.auth import UserCreate, UserResponse, Token, TokenRefreshRequest, LogoutRequest
from app.repositories.user_repository import UserRepository
from app.services.audit_logger import audit_logger
from app.core.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=Token)
@limiter.limit("3/minute")
def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if UserRepository.get_by_email(db, user.email) or UserRepository.get_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Email or Username already registered")
        
    # Create user
    db_user = UserRepository.create(db, user)
    
    # Create default settings for user
    db_settings = Settings(user_id=db_user.id)
    db.add(db_settings)
    db.commit()

    # Generate access & refresh tokens
    access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role})
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    refresh_token = create_refresh_token(db_user.id, db, client_ip=client_ip, user_agent=user_agent)

    audit_logger.log_action(db, "User Registered", user_id=db_user.id)

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = UserRepository.get_by_username(db, form_data.username)
    if not user:
        user = UserRepository.get_by_email(db, form_data.username)
        
    # Check if account is temporarily locked
    if user and user.locked_until:
        if datetime.utcnow() < user.locked_until:
            audit_logger.log_action(db, "Login Attempt on Locked Account", user_id=user.id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account temporarily locked due to repeated failed login attempts. Please try again later."
            )
        else:
            # Lockout expired, reset attempts
            user.locked_until = None
            user.failed_login_attempts = 0
            db.commit()

    if not user or not verify_password(form_data.password, user.password_hash):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                audit_logger.log_action(db, "Account Locked (Excessive Failures)", user_id=user.id)
            else:
                audit_logger.log_action(db, "Failed Login Attempt", user_id=user.id)
            db.commit()
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Reset failed login attempts on success
    if user.failed_login_attempts > 0 or user.locked_until is not None:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    refresh_token = create_refresh_token(user.id, db, client_ip=client_ip, user_agent=user_agent)

    audit_logger.log_action(db, "User Logged In", user_id=user.id)

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
def refresh_token_endpoint(request: Request, req: TokenRefreshRequest, db: Session = Depends(get_db)):
    token_h = hash_token(req.refresh_token)
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_h).first()
    
    if not db_token:
        logger.warning(f"Refresh attempt with unknown token from IP {request.client.host if request.client else 'unknown'}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Check revocation / reuse detection
    if db_token.revoked:
        # If someone reuses a revoked token, revoke all tokens for this user as a security precaution
        logger.error(f"Reuse of revoked refresh token detected for User ID {db_token.user_id}! Revoking all sessions.")
        db.query(RefreshToken).filter(RefreshToken.user_id == db_token.user_id).update({"revoked": True})
        db.commit()
        audit_logger.log_action(db, "Security Alert: Revoked Token Reuse", user_id=db_token.user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked due to suspected security violation",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if db_token.expires_at < datetime.utcnow():
        db_token.revoked = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")

    # Token Rotation: Revoke current refresh token and issue a new pair
    db_token.revoked = True
    
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    new_refresh_token = create_refresh_token(user.id, db, client_ip=client_ip, user_agent=user_agent)
    
    db_token.replaced_by = hash_token(new_refresh_token)
    db.commit()

    new_access_token = create_access_token(data={"sub": user.username, "role": user.role})
    audit_logger.log_action(db, "Token Refreshed", user_id=user.id)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token
    }

@router.post("/logout")
def logout(request: Request, req: LogoutRequest = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Revoke access token in server-side TTL cache
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token_str = auth_header.replace("Bearer ", "")
        revoke_token_from_cache(token_str)
        
    # 2. Revoke refresh token in DB if provided
    if req and req.refresh_token:
        token_h = hash_token(req.refresh_token)
        db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_h).first()
        if db_token and db_token.user_id == current_user.id:
            db_token.revoked = True
            db.commit()
    else:
        # If no specific refresh token provided, revoke all active refresh tokens for this user
        db.query(RefreshToken).filter(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked == False
        ).update({"revoked": True})
        db.commit()

    audit_logger.log_action(db, "User Logged Out", user_id=current_user.id)
    return {"status": "success", "message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
